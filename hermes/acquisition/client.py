from __future__ import annotations

import json as _json
import logging
import time
from collections.abc import Iterator
from typing import Any, TypeAlias
from urllib.parse import urljoin

import hermes._rust as _rust_module

_RustHttpClient: TypeAlias = _rust_module.http.HttpClient
_RustHttpResponse: TypeAlias = _rust_module.http.HttpResponse
HermesHttpError: TypeAlias = _rust_module.http.HermesHttpError
from hermes.core.errors import (
    AcquisitionError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class Client:
    """Synchronous HTTP client backed by the Hermes Rust core.

    Retries for transport faults and 5xx responses are handled by the Rust
    client (idempotent methods only). This layer maps status codes and raw
    errors onto Hermes error types.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 0,
        backoff_factor: float = 1.0,
        max_backoff: float = 60.0,
        headers: dict[str, str] | None = None,
        retry_auth: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.headers = headers or {}
        self.retry_auth = retry_auth
        self._client = self._build_client(timeout)

    def _build_client(self, timeout: float) -> _RustHttpClient:
        return _RustHttpClient(timeout_secs=timeout, retries=self.max_retries)

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client = None

    def get(self, url: str, **kwargs: Any) -> Any:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Any:
        return self.request("DELETE", url, **kwargs)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> Any:
        attempt = 0
        while True:
            try:
                resp = self._request_response(
                    method,
                    url,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    **kwargs,
                )
                self._raise_for_status(resp, url)
                return self._decode(resp)
            except AuthenticationError as exc:
                if not self.retry_auth:
                    raise
                err: Exception = exc
            attempt += 1
            if attempt > self.max_retries:
                raise err
            delay = self._retry_delay(attempt, err)
            logger.debug(
                "Request %s attempt %d failed (%s): retrying in %.2fs",
                url,
                attempt,
                type(err).__name__,
                delay,
            )
            if delay > 0:
                time.sleep(delay)

    def stream(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        chunk_size: int = 8192,
        **kwargs: Any,
    ) -> Iterator[bytes]:
        resp = self._request_response(method, url, params=params, headers=headers, **kwargs)
        self._raise_for_status(resp, url)
        body = resp.bytes()
        for offset in range(0, len(body), chunk_size):
            yield body[offset : offset + chunk_size]

    def _request_response(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs: Any,
    ) -> _RustHttpResponse:
        full_url = urljoin(self.base_url or "", url)
        body: str | None = None
        merged = {**self.headers, **(headers or {})}
        if json is not None:
            body = _json.dumps(json)
            merged.setdefault("Content-Type", "application/json")
        elif data is not None:
            if not isinstance(data, str):
                raise TypeError("data must be a str; send structured payloads via json=...")
            body = data
        client = self._client
        if client is None:
            client = self._build_client(self.timeout)
        if timeout is not None:
            client = self._build_client(timeout)
        try:
            return client.request(
                method,
                full_url,
                body=body,
                headers=list(merged.items()),
                query=list((k, str(v)) for k, v in params.items()) if params else None,
            )
        except HermesHttpError as exc:
            raise self._map_exception(exc, full_url) from exc

    @staticmethod
    def _decode(resp: _RustHttpResponse) -> Any:
        content_type = resp.header("content-type") or ""
        if "json" in content_type:
            return resp.json()
        if "text" in content_type:
            return resp.text()
        return resp.bytes()

    @staticmethod
    def _raise_for_status(resp: _RustHttpResponse, url: str) -> None:
        status = resp.status
        if status < 400:
            return
        try:
            body = resp.text()
        except Exception:
            body = ""
        if status in (401, 403):
            raise AuthenticationError(f"Auth error {status} on {url}: {body[:500]}", status_code=status)
        if status == 429:
            raw = resp.header("Retry-After")
            try:
                retry_after = float(raw) if raw else None
            except ValueError:
                retry_after = None
            error = RateLimitError(
                f"Rate limited on {url} (status 429). Retry-After={raw}. {body[:500]}",
                retry_after=retry_after,
            )
            error.status_code = status
            raise error
        if status >= 500:
            raise ServerError(f"Server error {status} on {url}: {body[:500]}", status_code=status)
        raise AcquisitionError(f"HTTP {status} on {url}: {body[:500]}", status_code=status)

    @staticmethod
    def _map_exception(exc: HermesHttpError, url: str) -> Exception:
        if getattr(exc, "category", None) == "Timeout":
            return TimeoutError(f"Request timed out on {url}")
        return AcquisitionError(
            f"Request failed on {url}: {exc}",
            status_code=getattr(exc, "status_code", None),
        )

    def _retry_delay(self, attempt: int, error: Exception) -> float:
        if isinstance(error, RateLimitError) and error.retry_after is not None:
            return min(error.retry_after, self.max_backoff)
        return min(self.backoff_factor * (2 ** (attempt - 1)), self.max_backoff)
