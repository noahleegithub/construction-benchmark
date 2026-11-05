"""Configuration helpers.

Loads a small ``.env`` file without adding a dependency. Existing environment
variables win, so a shell export always overrides the file.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_env(*paths: Path) -> None:
    for path in paths:
        if not path or not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def gateway_settings() -> tuple[str, str | None, dict[str, str]]:
    """Return (base_url, api_key, extra_headers) for the TAMU gateway."""
    base_url = os.environ.get("TAMU_GATEWAY_URL", "https://gateway.api.tamu.ai/v1")
    api_key = os.environ.get("TAMU_API_KEY") or None
    headers = {}
    client_id = os.environ.get("CF_ACCESS_CLIENT_ID")
    client_secret = os.environ.get("CF_ACCESS_CLIENT_SECRET")
    if client_id and client_secret:
        headers["CF-Access-Client-Id"] = client_id
        headers["CF-Access-Client-Secret"] = client_secret
    return base_url.rstrip("/"), api_key, headers
