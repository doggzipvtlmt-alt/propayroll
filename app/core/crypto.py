import base64
import hashlib
import secrets
import hmac

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


def verify_secret(secret: str, expected_hash: str | None, salt: str | None, iterations: int | None) -> bool:
    if not secret or not expected_hash or not salt or not iterations:
        return False
    try:
        salt_bytes = base64.b64decode(salt.encode("utf-8"))
        expected_bytes = base64.b64decode(expected_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
    derived = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt_bytes, iterations)
    return hmac.compare_digest(derived, expected_bytes)
