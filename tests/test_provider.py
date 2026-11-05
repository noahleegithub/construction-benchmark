import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from takeoff_bench.providers import OpenAICompatProvider
from takeoff_bench.schema import Item


def test_openai_compatible_request_and_response(monkeypatch):
    received = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers["Content-Length"])
            received["body"] = json.loads(self.rfile.read(length))
            received["auth"] = self.headers["Authorization"]
            received["cf_id"] = self.headers.get("CF-Access-Client-Id")
            received["cf_secret"] = self.headers.get("CF-Access-Client-Secret")
            payload = {
                "choices": [
                    {"message": {"content": '{"count": 3}'}, "finish_reason": "stop"}
                ],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            }
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format, *args):  # noqa: A002
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        monkeypatch.setenv("TEST_API_KEY", "secret")
        monkeypatch.setenv("CF_ACCESS_CLIENT_ID", "cf-id")
        monkeypatch.setenv("CF_ACCESS_CLIENT_SECRET", "cf-secret")
        provider = OpenAICompatProvider(
            {
                "model": "test-model",
                "base_url": f"http://127.0.0.1:{server.server_port}/v1",
                "api_key_env": "TEST_API_KEY",
                "temperature": None,
                "max_tokens": 512,
                "token_param": "max_completion_tokens",
                "input_cost_per_mtok": 1.0,
                "output_cost_per_mtok": 2.0,
            }
        )
        item = Item(
            item_id="x",
            family="f",
            sheet="s.pdf",
            page=1,
            question="q",
            convention="c",
            output_type="count",
            gt="g.json",
        )
        result = provider.complete(
            system="system", user="user", image_png=b"fake-png", item=item, gt={}
        )
    finally:
        server.shutdown()

    assert result.error is None
    assert result.text == '{"count": 3}'
    assert result.usage["finish_reason"] == "stop"
    assert result.cost_usd == (100 / 1e6 * 1.0) + (20 / 1e6 * 2.0)

    body = received["body"]
    assert body["model"] == "test-model"
    assert body["max_completion_tokens"] == 512
    assert "temperature" not in body
    assert body["messages"][0] == {"role": "system", "content": "system"}
    assert received["auth"] == "Bearer secret"
    assert received["cf_id"] == "cf-id"
    assert received["cf_secret"] == "cf-secret"
    content = body["messages"][1]["content"]
    assert content[0] == {"type": "text", "text": "user"}
    url = content[1]["image_url"]["url"]
    assert url.startswith("data:image/png;base64,")
    assert base64.b64decode(url.split(",", 1)[1]) == b"fake-png"
