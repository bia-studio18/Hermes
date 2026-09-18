from typing import Any

from hermes.credentials.storage import CredentialNotFoundError, load_credentials, write_credentials


def set_cred(name: str, value: Any) -> None:
    if not name:
        raise ValueError("Credential name cannot be empty.")

    credentials = load_credentials()
    credentials[name] = value
    write_credentials(credentials)


def get_cred(name: str) -> Any:
    credentials = load_credentials()

    if name not in credentials:
        raise CredentialNotFoundError(f"Credential '{name}' does not exist.")

    return credentials[name]


def has_cred(name: str) -> bool:
    credentials = load_credentials()
    return name in credentials


def delete_cred(name: str) -> None:
    credentials = load_credentials()

    if name not in credentials:
        raise CredentialNotFoundError(f"Credential '{name}' does not exist.")

    del credentials[name]
    write_credentials(credentials)


def list_creds() -> list[str]:
    credentials = load_credentials()
    return list(credentials.keys())
