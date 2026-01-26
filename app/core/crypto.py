import base64
import hashlib
import secrets

PBKDF2_ITERATIONS = 120_000


def hash_secret(secret: str) -> dict:
    if secret is None:
        return {}
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "hash": base64.b64encode(derived).decode("utf-8"),
        "iterations": PBKDF2_ITERATIONS,
    }


def mask_secret(secret: str | None) -> str | None:
    if not secret:
        return None
    return "********"
