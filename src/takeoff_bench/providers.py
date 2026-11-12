"""Model providers.

Only one wire format is implemented: the OpenAI-compatible chat completions
API. That covers OpenAI, OpenRouter, vLLM, and most hosted endpoints, which is
enough for a benchmark harness that should stay small. Anthropic's native API
can be reached through an OpenAI-compatible gateway.

Two offline providers exist for testing: ``stub`` returns empty outputs and
``oracle`` returns the ground truth, so the full run -> score pipeline can be
exercised without a network call.
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .schema import Item


@dataclass
class ProviderResult:
    text: str | None = None
    error: str | None = None
    latency_ms: int = 0
    usage: dict[str, Any] = field(default_factory=dict)
    cost_usd: float | None = None


class Provider:
    def complete(
        self,
        *,
        system: str,
        user: str,
        image_png: bytes,
        item: Item,
        gt: dict[str, Any],
    ) -> ProviderResult:
        raise NotImplementedError


class StubProvider(Provider):
    """Empty but schema-valid outputs. Useful for dry runs and CI."""

    def __init__(self, output_type: str | None = None):
        self.output_type = output_type

    def complete(self, *, system, user, image_png, item, gt):
        start = time.monotonic()
        out = {
            "polygons": {"instances": []},
            "polylines": {"lines": []},
            "points": {"points": []},
            "count": {"count": 0},
            "text": {"answer": ""},
            "quantities": {"line_items": []},
            "compliance": {"instances": []},
        }[item.output_type]
        return ProviderResult(
            text=json.dumps(out),
            latency_ms=int((time.monotonic() - start) * 1000),
        )


class OracleProvider(Provider):
    """Returns the ground truth verbatim. Test-only; never use for results."""

    def __init__(self, output_type: str | None = None):
        self.output_type = output_type

    def complete(self, *, system, user, image_png, item, gt):
        start = time.monotonic()
        return ProviderResult(
            text=json.dumps(gt),
            latency_ms=int((time.monotonic() - start) * 1000),
        )


class OpenAICompatProvider(Provider):
    def __init__(self, config: dict[str, Any]):
        self.model = os.path.expandvars(config["model"])
        if not self.model:
            raise ValueError("model id is empty; set the model in models.yaml or .env")
        self.base_url = os.path.expandvars(
            config.get("base_url", "https://api.openai.com/v1")
        ).rstrip("/")
        self.api_key_env = config.get("api_key_env", "OPENAI_API_KEY")
        temperature = config.get("temperature", 0)
        self.temperature = None if temperature is None else float(temperature)
        self.max_tokens = int(config.get("max_tokens", 8000))
        self.token_param = config.get("token_param", "max_tokens")
        self.detail = config.get("detail", "high")
        self.timeout = float(config.get("timeout", 300))
        self.input_cost = config.get("input_cost_per_mtok")
        self.output_cost = config.get("output_cost_per_mtok")
        self.extra = dict(config.get("extra", {}))
        self.extra_headers = dict(config.get("extra_headers", {}))

        key = os.environ.get(self.api_key_env)
        if not key:
            raise ValueError(
                f"{self.api_key_env} is not set (needed for model {self.model})"
            )
        self.api_key = key

    def complete(self, *, system, user, image_png, item, gt):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64,"
                                + base64.b64encode(image_png).decode("ascii"),
                                "detail": self.detail,
                            },
                        },
                    ],
                },
            ],
            self.token_param: self.max_tokens,
            **self.extra,
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        client_id = os.environ.get("CF_ACCESS_CLIENT_ID")
        client_secret = os.environ.get("CF_ACCESS_CLIENT_SECRET")
        if client_id and client_secret:
            headers["CF-Access-Client-Id"] = client_id
            headers["CF-Access-Client-Secret"] = client_secret
        headers.update(self.extra_headers)
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers=headers,
            method="POST",
        )

        start = time.monotonic()
        last_error = "request failed"
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                return self._result(body, start)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:500]
                last_error = f"HTTP {exc.code}: {detail}"
                if exc.code not in (408, 409, 429, 500, 502, 503, 504):
                    break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

        return ProviderResult(
            error=last_error,
            latency_ms=int((time.monotonic() - start) * 1000),
        )

    def _result(self, body: dict[str, Any], start: float) -> ProviderResult:
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            )
        if not isinstance(content, str):
            content = None

        usage = body.get("usage") or {}
        usage["finish_reason"] = choice.get("finish_reason")
        cost = None
        for candidate in (body.get("cost"), usage.get("cost"), usage.get("total_cost")):
            if isinstance(candidate, (int, float)):
                cost = float(candidate)
                break
        if cost is None and self.input_cost is not None and self.output_cost is not None:
            cost = (
                usage.get("prompt_tokens", 0) / 1e6 * float(self.input_cost)
                + usage.get("completion_tokens", 0) / 1e6 * float(self.output_cost)
            )
        return ProviderResult(
            text=content,
            latency_ms=int((time.monotonic() - start) * 1000),
            usage=usage,
            cost_usd=cost,
        )


def list_models(
    base_url: str,
    api_key: str,
    extra_headers: dict[str, str] | None = None,
    timeout: float = 30,
) -> list[dict[str, Any]]:
    """List model ids from an OpenAI-compatible endpoint."""
    headers = {"Authorization": f"Bearer {api_key}"}
    headers.update(extra_headers or {})
    request = urllib.request.Request(f"{base_url.rstrip('/')}/models", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise ValueError(f"HTTP {exc.code} from /models: {body}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"could not reach {base_url}: {exc}") from exc

    data = payload.get("data", payload if isinstance(payload, list) else [])
    return [entry for entry in data if isinstance(entry, dict) and entry.get("id")]


def build_provider(name: str, config: dict[str, Any] | None = None) -> Provider:
    if name == "stub":
        return StubProvider()
    if name == "oracle":
        return OracleProvider()
    if name in ("openai", "openai-compatible", "openrouter"):
        if not config:
            raise ValueError(f"provider {name} needs model configuration")
        return OpenAICompatProvider(config)
    raise ValueError(f"unknown provider: {name}")
