from __future__ import annotations

import json
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from hermes.acquisition.client import Client
from hermes.core.errors import AcquisitionError, AuthenticationError, RateLimitError

Route = tuple[int, dict[str, str], bytes]
RouteValue = Route | list[Route] | Callable[[int], Route]


class _Handler(BaseHTTPRequestHandler):
    routes: dict[tuple[str, str], RouteValue] = {}

    def _serve(self) -> None:
        route_value = self.routes.get((self.command, self.path))
        if route_value is None:
            self.send_response(404)
            self.end_headers()
            return
        if isinstance(route_value, list):
            if len(route_value) > 1:
                route = route_value.pop(0)
            else:
                route = route_value[0]
        elif callable(route_value):
            route = route_value(self.command)
        else:
            route = route_value
        status, headers, body = route
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._serve()

    def do_POST(self) -> None:
        self._serve()

    def do_PUT(self) -> None:
        self._serve()

    def do_DELETE(self) -> None:
        self._serve()

    def log_message(self, *args: Any) -> None:
        pass


def _json_response(payload: Any, status: int = 200, headers: dict[str, str] | None = None) -> Route:
    body = json.dumps(payload).encode()
    return status, {"Content-Type": "application/json", **(headers or {})}, body


@pytest.fixture
def http_server():
    """Start a threaded HTTP server serving canned routes configured via ``_Handler.routes``."""
    _Handler.routes = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_address[1]}"
    yield base_url
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


class TestClientRequests:
    async def test_get_returns_json(self, http_server):
        _Handler.routes[("GET", "/items")] = _json_response({"data": [1, 2, 3]})
        async with Client(base_url=http_server) as c:
            result = await c.get("/items")
        assert result == {"data": [1, 2, 3]}

    async def test_post_sends_json(self, http_server):
        _Handler.routes[("POST", "/items")] = _json_response({"created": True})
        async with Client(base_url=http_server) as c:
            result = await c.post("/items", json={"name": "x"})
        assert result == {"created": True}

    async def test_put_and_delete(self, http_server):
        _Handler.routes[("PUT", "/items/1")] = _json_response({"ok": True})
        _Handler.routes[("DELETE", "/items/1")] = _json_response({"deleted": True})
        async with Client(base_url=http_server) as c:
            assert await c.put("/items/1") == {"ok": True}
            assert await c.delete("/items/1") == {"deleted": True}

    async def test_query_params_passed(self, http_server):
        _Handler.routes[("GET", "/search?q=hermes&limit=5")] = _json_response({"results": []})
        async with Client(base_url=http_server) as c:
            result = await c.get("/search", params={"q": "hermes", "limit": 5})
        assert result == {"results": []}

    async def test_client_error_not_retried_by_default(self, http_server):
        _Handler.routes[("GET", "/items")] = (400, {"Content-Type": "text/plain"}, b"bad")
        async with Client(base_url=http_server) as c:
            with pytest.raises(AcquisitionError):
                await c.get("/items")

    async def test_retries_until_success(self, http_server):
        _Handler.routes[("GET", "/items")] = [
            (503, {"Content-Type": "text/plain"}, b"first"),
            (503, {"Content-Type": "text/plain"}, b"second"),
            _json_response({"ok": True}),
        ]
        async with Client(base_url=http_server, max_retries=3, backoff_factor=0.01) as c:
            result = await c.get("/items")
        assert result == {"ok": True}

    async def test_gives_up_after_max_retries(self, http_server):
        _Handler.routes[("GET", "/items")] = [(503, {"Content-Type": "text/plain"}, b"unavailable")]
        async with Client(base_url=http_server, max_retries=2, backoff_factor=0.01) as c:
            with pytest.raises(AcquisitionError):
                await c.get("/items")

    async def test_auth_error_raised(self, http_server):
        _Handler.routes[("GET", "/secure")] = (401, {"Content-Type": "text/plain"}, b"denied")
        async with Client(base_url=http_server) as c:
            with pytest.raises(AuthenticationError):
                await c.get("/secure")

    async def test_auth_error_not_retried(self, http_server):
        _Handler.routes[("GET", "/secure")] = (403, {"Content-Type": "text/plain"}, b"denied")
        async with Client(base_url=http_server, max_retries=5) as c:
            with pytest.raises(AuthenticationError):
                await c.get("/secure")

    async def test_rate_limit_error_raised(self, http_server):
        _Handler.routes[("GET", "/items")] = (
            429,
            {"Content-Type": "text/plain", "Retry-After": "3"},
            b"slow down",
        )
        async with Client(base_url=http_server) as c:
            with pytest.raises(RateLimitError) as ei:
                await c.get("/items")
            assert ei.value.retry_after == 3.0


class TestClientStream:
    async def test_stream_chunks(self, http_server):
        _Handler.routes[("GET", "/blob")] = (
            200,
            {"Content-Type": "application/octet-stream"},
            b"abcdefghij",
        )
        async with Client(base_url=http_server) as c:
            chunks = [chunk async for chunk in c.stream("GET", "/blob", chunk_size=4)]
        assert chunks == [b"abcd", b"efgh", b"ij"]


class TestClientLifecycle:
    async def test_request_before_open_raises(self):
        c = Client(base_url="http://example.com")  # not used as context manager
        with pytest.raises(AcquisitionError):
            await c.get("/x")
        await c.close()

    async def test_close_twice_is_safe(self, http_server):
        async with Client(base_url=http_server) as c:
            await c.close()
            await c.close()
