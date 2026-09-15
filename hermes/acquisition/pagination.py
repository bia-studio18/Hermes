from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel

from hermes.core.errors import AcquisitionError

logger = logging.getLogger(__name__)


class Page(BaseModel):
    data: Any
    has_more: bool
    next_params: dict[str, Any] | str | None = None


class Paginator:
    STRATEGIES = ("page", "offset", "cursor", "next_url", "date_range", "token")

    def __init__(self, strategy: str = "page") -> None:
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown pagination strategy {strategy!r}; expected one of {self.STRATEGIES}")
        self.strategy = strategy

    async def paginate(
        self,
        fetch_fn: Callable[..., Any],
        *,
        max_pages: int | None = None,
        page_size: int = 100,
        initial_cursor: Any | None = None,
        initial_url: str | None = None,
        initial_token: Any | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        date_delta: timedelta = timedelta(days=1),
        **kwargs: Any,
    ) -> list[Any]:

        results: list[Any] = []
        seen: set[Any] = set()
        page_no = 0

        state = self._init_state(
            page_size=page_size,
            initial_cursor=initial_cursor,
            initial_url=initial_url,
            initial_token=initial_token,
            start_date=start_date,
            end_date=end_date,
            date_delta=date_delta,
        )

        while True:
            if max_pages is not None and page_no >= max_pages:
                logger.debug("Stopped pagination after %d page(s) (max_pages)", page_no)
                break
            if state is None:
                break

            params = self._build_params(state, page_size)
            page = await self._call_fetch(fetch_fn, params, **kwargs)
            results.extend(list(page.data))
            page_no += 1

            if not self._should_continue(page, page_no, max_pages):
                break

            # Cursor/token/next-url strategies need the page to supply them.
            if self.strategy in ("cursor", "token", "next_url"):
                if page.next_params is None:
                    break
                key = self._fingerprint(page.next_params)
                if key in seen:
                    logger.warning("Pagination loop detected; stopping at page %d", page_no)
                    break
                seen.add(key)

            state = self._advance_state(state, page.next_params, page_size)
            if state is None:
                break

        logger.debug(
            "Paginator (%s) fetched %d items across %d page(s)",
            self.strategy,
            len(results),
            page_no,
        )
        return results

    @staticmethod
    async def _call_fetch(fetch_fn: Callable[..., Any], params: dict[str, Any], **kwargs: Any) -> Page:
        try:
            page = await fetch_fn(**params, **kwargs)
        except TypeError:
            page = await fetch_fn(params, **kwargs)
        return Paginator._coerce_page(page)

    def _should_continue(self, page: Page, page_no: int, max_pages: int | None) -> bool:
        """Decide whether another page should be fetched.

        The ``date_range`` strategy continues until the state window is
        exhausted; all other strategies follow the response's ``has_more``.
        """
        if max_pages is not None and page_no >= max_pages:
            return False
        if self.strategy == "date_range":
            return True
        return page.has_more

    def _init_state(
        self,
        *,
        page_size: int,
        initial_cursor: Any | None,
        initial_url: str | None,
        initial_token: Any | None,
        start_date: datetime | None,
        end_date: datetime | None,
        date_delta: timedelta,
    ) -> dict[str, Any] | None:
        if self.strategy == "page":
            return {"page": 1}
        if self.strategy == "offset":
            return {"offset": 0}
        if self.strategy == "cursor":
            return {"cursor": initial_cursor}
        if self.strategy == "next_url":
            if initial_url is None:
                raise AcquisitionError("Paginator(strategy='next_url') requires initial_url")
            return {"url": initial_url}
        if self.strategy == "token":
            return {"token": initial_token}
        if self.strategy == "date_range":
            if start_date is None or end_date is None:
                raise AcquisitionError("Paginator(strategy='date_range') requires start_date and end_date")
            return {
                "cursor_date": start_date,
                "end_date": end_date,
                "delta": date_delta,
            }
        raise AssertionError(f"Unhandled strategy {self.strategy}")

    def _build_params(self, state: dict[str, Any], page_size: int) -> dict[str, Any]:
        if self.strategy == "page":
            return {"page": state["page"], "page_size": page_size}
        if self.strategy == "offset":
            return {"offset": state["offset"], "limit": page_size}
        if self.strategy == "cursor":
            return {"cursor": state.get("cursor")}
        if self.strategy == "next_url":
            return {"url": state["url"]}
        if self.strategy == "token":
            return {"token": state.get("token")}
        if self.strategy == "date_range":
            cursor = state["cursor_date"]
            end: datetime = state["end_date"]
            d: timedelta = state["delta"]
            return {"start_date": cursor, "end_date": min(cursor + d, end)}
        raise AssertionError(f"Unhandled strategy {self.strategy}")

    def _advance_state(
        self,
        state: dict[str, Any],
        next_params: dict[str, Any] | str | None,
        page_size: int,
    ) -> dict[str, Any] | None:
        if self.strategy == "page":
            return {"page": state["page"] + 1}
        if self.strategy == "offset":
            return {"offset": state["offset"] + page_size}
        if self.strategy == "date_range":
            next_date = state["cursor_date"] + state["delta"]
            if next_date > state["end_date"]:
                return None
            return {**state, "cursor_date": next_date}
        if self.strategy == "next_url":
            if not isinstance(next_params, str) or not next_params:
                return None
            return {"url": next_params}

        if isinstance(next_params, dict):
            value = next_params.get("cursor", next_params.get("token"))
        else:
            value = next_params
        if value is None:
            return None
        key = "cursor" if self.strategy == "cursor" else "token"
        return {key: value}

    @staticmethod
    def _coerce_page(page: Any) -> Page:
        """Normalize the value returned by ``fetch_fn`` into a :class:`Page`."""
        if isinstance(page, Page):
            return page
        if isinstance(page, tuple):
            if len(page) == 2:
                return Page(data=page[0], has_more=bool(page[1]))
            if len(page) == 3:
                return Page(data=page[0], has_more=bool(page[1]), next_params=page[2])
        raise AcquisitionError(f"fetch_fn must return a Page or a (data, has_more[, next]) tuple, got {type(page)!r}")

    @staticmethod
    def _fingerprint(params: dict[str, Any] | str) -> str:
        if isinstance(params, str):
            return params
        import json

        return json.dumps(params, sort_keys=True, default=str)
