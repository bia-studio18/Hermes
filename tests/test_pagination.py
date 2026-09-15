from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from hermes.acquisition.pagination import Page, Paginator
from hermes.core.errors import AcquisitionError


async def _page_source(data: list, page_size: int = 3):
    """Async fetch_fn for a page-based API returning (records, has_more)."""

    async def fetch_fn(page: int, page_size: int = page_size, **kwargs):
        start = (page - 1) * page_size
        chunk = data[start : start + page_size]
        return chunk, len(chunk) == page_size and start + page_size < len(data)

    return fetch_fn


class TestPageBased:
    async def test_paginates_all_items(self):
        data = list(range(10))
        page = Paginator(strategy="page")
        result = await page.paginate(await _page_source(data), page_size=3)
        assert result == data

    async def test_respects_max_pages(self):
        data = list(range(20))
        page = Paginator(strategy="page")
        result = await page.paginate(await _page_source(data), page_size=3, max_pages=2)
        assert result == data[:6]  # two pages of 3

    async def test_page_size_override(self):
        data = list(range(10))
        page = Paginator(strategy="page")
        result = await page.paginate(
            await _page_source(data, page_size=5),
            page_size=5,
            max_pages=2,
        )
        assert result == data[:10]


class TestOffsetBased:
    async def test_offset_pagination(self):
        data = list(range(10))

        async def fetch_fn(offset: int, limit: int, **kwargs):
            chunk = data[offset : offset + limit]
            return chunk, offset + limit < len(data)

        result = await Paginator(strategy="offset").paginate(fetch_fn, page_size=4)
        assert result == data


class TestCursorBased:
    async def test_cursor_pagination(self):
        pages = {
            None: (["a", "b", "c"], "curs1"),
            "curs1": (["d", "e", "f"], "curs2"),
            "curs2": (["g"], None),
        }

        async def fetch_fn(cursor, **kwargs):
            items, next_cursor = pages[cursor]
            return Page(data=items, has_more=next_cursor is not None, next_params=next_cursor)

        result = await Paginator(strategy="cursor").paginate(fetch_fn)
        assert result == ["a", "b", "c", "d", "e", "f", "g"]


class TestNextUrlBased:
    async def test_next_url_pagination(self):
        urls = {
            "start": (["one"], "two"),
            "two": (["three"], None),
        }

        async def fetch_fn(url, **kwargs):
            items, nxt = urls[url]
            return items, nxt is not None, nxt

        result = await Paginator(strategy="next_url").paginate(fetch_fn, initial_url="start")
        assert result == ["one", "three"]

    async def test_missing_initial_url_raises(self):
        async def fetch_fn(**kwargs):
            return [], False

        with pytest.raises(AcquisitionError):
            await Paginator(strategy="next_url").paginate(fetch_fn)


class TestDateRangeBased:
    async def test_date_range_slicing(self):
        start = datetime(2026, 1, 1)
        end = datetime(2026, 1, 5)
        windows: list[tuple] = []

        async def fetch_fn(start_date, end_date, **kwargs):
            windows.append((start_date, end_date))
            return [start_date.date().isoformat()], False

        result = await Paginator(strategy="date_range").paginate(
            fetch_fn,
            start_date=start,
            end_date=end,
            date_delta=timedelta(days=2),
        )
        assert len(result) == 3  # three windows: 1-3, 3-5, capped
        assert (windows[0][0], windows[0][1]) == (start, datetime(2026, 1, 3))
        assert (windows[-1][0], windows[-1][1]) == (datetime(2026, 1, 5), end)

    async def test_requires_dates(self):
        async def fetch_fn(**kwargs):
            return [], False

        with pytest.raises(AcquisitionError):
            await Paginator(strategy="date_range").paginate(fetch_fn)


class TestRobustness:
    async def test_loop_detection(self):
        async def fetch_fn(page, **kwargs):
            return [page], True, {"same": "value"}

        # cursor-less page strategy advances regardless, so use max_pages
        result = await Paginator(strategy="cursor").paginate(fake_loop_fetch_fn, max_pages=3)

    async def test_invalid_strategy_raises(self):
        with pytest.raises(ValueError):
            Paginator(strategy="bogus")

    async def test_bad_fetch_fn_return_raises(self):
        async def fetch_fn(**kwargs):
            return 12345

        with pytest.raises(AcquisitionError):
            await Paginator(strategy="page").paginate(fetch_fn)

    async def test_accepts_two_or_three_tuple(self):
        async def two_tuple(page, **kwargs):
            return [1, 2], False

        assert await Paginator(strategy="page").paginate(two_tuple) == [1, 2]

        async def three_tuple(page, **kwargs):
            if page >= 2:
                return [3], False, None
            return [3], True, None

        assert await Paginator(strategy="page").paginate(three_tuple) == [3, 3]


async def fake_loop_fetch_fn(cursor, **kwargs):
    return Page(data=[cursor], has_more=True, next_params="loop")
