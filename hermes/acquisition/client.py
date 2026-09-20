from __future__ import annotations

import asyncio
import builtins
import logging
from collections.abc import AsyncIterator
from typing import Any

import aiohttp

from hermes.core.errors import (
    AcquisitionError,
    AuthenticationError,
    RateLimitError,
    ServerError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 0,
        backoff_factor: float = 1.0,
        max_backoff: float = 60.0,
        headers: dict[str, str] | None = None,
        connector: aiohttp.BaseConnector | None = None,
        retry_auth: bool = False,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.headers = headers or {}
        self.retry_auth = retry_auth
        self._connector = connector
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Client:
        self._session = aiohttp.ClientSession(
            base_url=self.base_url or None,
            headers=self.headers,
            timeout=self.timeout,
            connector=self._connector,
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise AcquisitionError("Client is not open. Use 'async with Client() as c:'.")
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get(self, url: str, **kwargs: Any) -> Any:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> Any:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs: Any) -> Any:
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs: Any) -> Any:
        return await self.request("DELETE", url, **kwargs)

    async def request(
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
        merged_headers = {**self.headers, **(headers or {})}
        req_timeout = aiohttp.ClientTimeout(total=timeout) if timeout is not None else None

        attempt = 0
        while True:
            try:
                async with self.session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    data=data,
                    headers=merged_headers or None,
                    timeout=req_timeout,
                    **kwargs,
                ) as resp:
                    await self._raise_for_status(resp, url)
                    return await self._decode(resp)
            except AuthenticationError as exc:
                if not self.retry_auth:
                    raise
                err: Exception = exc
            except (
                aiohttp.ClientError,
                TimeoutError,
                ServerError,
                RateLimitError,
                builtins.TimeoutError,
            ) as exc:
                err = exc
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
                await asyncio.sleep(delay)

    async def stream(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        chunk_size: int = 8192,
        **kwargs: Any,
    ) -> AsyncIterator[bytes]:
        merged_headers = {**self.headers, **(headers or {})}
        async with self.session.request(
            method,
            url,
            params=params,
            headers=merged_headers or None,
            **kwargs,
        ) as resp:
            await self._raise_for_status(resp, url)
            async for chunk in resp.content.iter_chunked(chunk_size):
                yield chunk

    @staticmethod
    async def _decode(resp: aiohttp.ClientResponse) -> Any:
        content_type = resp.content_type or ""
        if "json" in content_type:
            return await resp.json()
        if "text" in content_type:
            return await resp.text()
        return await resp.read()

    @staticmethod
    async def _raise_for_status(resp: aiohttp.ClientResponse, url: str) -> None:
        if resp.status < 400:
            return
        body = await resp.text(errors="replace")
        if resp.status in (401, 403):
            raise AuthenticationError(f"Auth error {resp.status} on {url}: {body[:500]}", status_code=resp.status)
        if resp.status == 429:
            raw = resp.headers.get("Retry-After")
            try:
                retry_after = float(raw) if raw else None
            except ValueError:
                retry_after = None
            error = RateLimitError(
                f"Rate limited on {url} (status 429). Retry-After={raw}. {body[:500]}",
                retry_after=retry_after,
            )
            error.status_code = resp.status
            raise error
        if resp.status >= 500:
            raise ServerError(f"Server error {resp.status} on {url}: {body[:500]}", status_code=resp.status)
        raise AcquisitionError(f"HTTP {resp.status} on {url}: {body[:500]}", status_code=resp.status)

    def _retry_delay(self, attempt: int, error: Exception) -> float:
        if isinstance(error, RateLimitError) and error.retry_after is not None:
            return min(error.retry_after, self.max_backoff)
        return min(self.backoff_factor * (2 ** (attempt - 1)), self.max_backoff)
