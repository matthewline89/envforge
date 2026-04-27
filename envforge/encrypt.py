"""Encryption support for snapshots using Fernet symmetric encryption."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "cryptography package is required for encryption support. "
        "Install it with: pip install cryptography"
    ) from exc


KEY_ENV_VAR = "ENVFORGE_KEY"


def generate_key() -> str:
    """Generate a new Fernet key and return it as a string."""
    return Fernet.generate_key().decode()


def _get_fernet(key: str | None = None) -> Fernet:
    """Return a Fernet instance using the provided key or ENVFORGE_KEY env var."""
    resolved = key or os.environ.get(KEY_ENV_VAR)
    if not resolved:
        raise ValueError(
            f"No encryption key provided. Set {KEY_ENV_VAR} or pass key explicitly."
        )
    return Fernet(resolved.encode() if isinstance(resolved, str) else resolved)


def encrypt_snapshot(data: dict, key: str | None = None) -> bytes:
    """Serialize and encrypt a snapshot dict, returning ciphertext bytes."""
    fernet = _get_fernet(key)
    plaintext = json.dumps(data).encode()
    return fernet.encrypt(plaintext)


def decrypt_snapshot(ciphertext: bytes, key: str | None = None) -> dict:
    """Decrypt ciphertext and return the original snapshot dict."""
    fernet = _get_fernet(key)
    try:
        plaintext = fernet.decrypt(ciphertext)
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid key or corrupted data.") from exc
    return json.loads(plaintext.decode())


def save_encrypted(data: dict, path: Path, key: str | None = None) -> None:
    """Encrypt *data* and write ciphertext to *path*."""
    ciphertext = encrypt_snapshot(data, key)
    path.write_bytes(ciphertext)


def load_encrypted(path: Path, key: str | None = None) -> dict:
    """Read ciphertext from *path* and return the decrypted snapshot dict."""
    ciphertext = path.read_bytes()
    return decrypt_snapshot(ciphertext, key)
