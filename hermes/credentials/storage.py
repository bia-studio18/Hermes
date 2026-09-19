from __future__ import annotations

import json
from pathlib import Path
from typing import Any

HERMES_HOME = Path.home() / ".hermes-plt"
CREDENTIALS_FILE = HERMES_HOME / "credentials.json"


class CredentialError(Exception):
    """Base exception for credential errors."""


class CredentialNotFoundError(CredentialError):
    """Raised when a credential does not exist."""


class CredentialStorageError(CredentialError):
    """Raised when the credential store cannot be read or written."""


def init_credentials() -> Path:
    try:
        HERMES_HOME.mkdir(parents=True, exist_ok=True)

        if not CREDENTIALS_FILE.exists():
            CREDENTIALS_FILE.write_text(
                "{}\n",
                encoding="utf-8",
            )

            CREDENTIALS_FILE.chmod(0o600)

    except OSError as exc:
        raise CredentialStorageError(f"Could not initialize credential store: {exc}") from exc

    return CREDENTIALS_FILE


def load_credentials() -> dict[str, Any]:
    if not CREDENTIALS_FILE.exists():
        raise CredentialStorageError("Hermes credentials are not initialized. Run `hermes cred init` first.")

    try:
        with CREDENTIALS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise CredentialStorageError(f"Invalid credentials file: {CREDENTIALS_FILE}") from exc
    except OSError as exc:
        raise CredentialStorageError(f"Could not read credentials: {exc}") from exc

    if not isinstance(data, dict):
        raise CredentialStorageError("credentials.json must contain a JSON object.")

    return data


def write_credentials(credentials: dict[str, Any]) -> None:
    try:
        HERMES_HOME.mkdir(parents=True, exist_ok=True)

        with CREDENTIALS_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                credentials,
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.write("\n")

        CREDENTIALS_FILE.chmod(0o600)

    except OSError as exc:
        raise CredentialStorageError(f"Could not write credentials: {exc}") from exc
