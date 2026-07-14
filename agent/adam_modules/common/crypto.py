"""
FieldCipher — szyfrowanie pól PII (PESEL, telefon) zgodnie z RODO.

Używa Fernet (AES-128-CBC + HMAC-SHA256, authenticated encryption) z biblioteki
`cryptography`. Klucz z ADAM_PII_KEY (base64 32B) — w produkcji z sejfu/KMS.

Uwaga nazewnicza: MASTER-PLAN mówi „AES-256"; Fernet daje AES-128 w trybie CBC
z uwierzytelnianiem HMAC-SHA256. Dla ścisłego AES-256-GCM można podmienić
implementację na AESGCM — interfejs FieldCipher pozostaje ten sam.
"""
from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken


def _derive_key(secret: str) -> bytes:
    """Zwraca 32-bajtowy klucz Fernet z sekretu (dozwolony też gotowy klucz base64)."""
    # Jeśli sekret jest już poprawnym kluczem Fernet (44 znaki base64) — użyj wprost.
    try:
        raw = base64.urlsafe_b64decode(secret)
        if len(raw) == 32:
            return secret.encode()
    except Exception:
        pass
    # W przeciwnym razie wyprowadź deterministycznie (SHA-256 → 32B → base64url).
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


class FieldCipher:
    """Szyfruje/odszyfrowuje pojedyncze pola tekstowe."""

    def __init__(self, secret: str | None = None):
        secret = secret or os.getenv("ADAM_PII_KEY", "adam-dev-insecure-key-change-me")
        self._fernet = Fernet(_derive_key(secret))

    def encrypt(self, plaintext: str | None) -> str | None:
        if plaintext is None:
            return None
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str | None) -> str | None:
        if token is None:
            return None
        try:
            return self._fernet.decrypt(token.encode()).decode()
        except InvalidToken:
            raise ValueError("Nie można odszyfrować pola PII — nieprawidłowy klucz lub token")

    @staticmethod
    def blind_index(value: str) -> str:
        """
        Deterministyczny hash do wyszukiwania po zaszyfrowanym polu (blind index).
        Pozwala szukać np. po PESEL bez przechowywania go jawnie.
        """
        pepper = os.getenv("ADAM_PII_PEPPER", "adam-pepper")
        return hashlib.sha256((pepper + value).encode()).hexdigest()


_cipher: FieldCipher | None = None


def get_cipher() -> FieldCipher:
    global _cipher
    if _cipher is None:
        _cipher = FieldCipher()
    return _cipher
