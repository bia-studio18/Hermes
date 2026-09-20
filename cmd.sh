export RUFF_CACHE_DIR=/tmp/ruff_cache

uv run pytest
uv run ruff check . --fix
uv run ruff check . 
uv run ruff format .
uv run mypy hermes