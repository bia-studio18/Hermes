import os
from pathlib import Path

API_SOURCES = ["fred", "opensanctions", "newsdata"]


class HermesConfig:
    def __init__(self) -> None:
        self._api_keys: dict[str, str] = {}
        self._settings: dict[str, str] = {}

    def set_api_key(self, source: str, key: str) -> None:
        self._api_keys[source] = key

    def get_api_key(self, source: str) -> str | None:
        return self._api_keys[source]

    def requires_api_key(self, source: str) -> bool:
        req: list[str] = API_SOURCES

        if source in req:
            return True
        else:
            return False

    @property
    def storage_root(self) -> str:
        """Storage root: explicit setting > HERMES_STORAGE_ROOT env var > default."""
        for value in (self._settings.get("storage_root"), os.environ.get("HERMES_STORAGE_ROOT")):
            if value:
                return value
        return str(Path.home() / ".hermes-plt" / "storage")

    def resolve_config(self, source: str) -> dict[str, str]:
        raise NotImplementedError()


_config: HermesConfig | None = None


def configure(api_keys: dict[str, str] | None = None, **settings: str) -> HermesConfig:
    global _config
    config = HermesConfig()
    if api_keys:
        for source, key in api_keys.items():
            config.set_api_key(source, key)
    for key, value in settings.items():
        config._settings[key] = value
    _config = config
    return config


def get_config() -> HermesConfig:
    global _config
    if _config is None:
        _config = HermesConfig()
    return _config
