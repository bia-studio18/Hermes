import unicodedata


def _normalize(value: str) -> str:
    value = str(value)
    value = unicodedata.normalize("NFKC", value)
    value = value.strip()
    value = value.casefold()
    return value


def exact(given: str, candidate: str) -> float:
    return 1.0 if _normalize(given) == _normalize(candidate) else 0.0