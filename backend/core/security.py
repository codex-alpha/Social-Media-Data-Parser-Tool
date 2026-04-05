"""Security utilities: hashing, JWT tokens, encryption."""
import hashlib
import json
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def sha256_hash(data: Any) -> str:
    """Generate SHA-256 hash for any data (used for forensic integrity)."""
    if isinstance(data, dict) or isinstance(data, list):
        data_str = json.dumps(data, sort_keys=True, default=str)
    elif isinstance(data, bytes):
        data_str = data.decode("utf-8", errors="replace")
    else:
        data_str = str(data)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def hmac_sign(data: str, key: Optional[str] = None) -> str:
    """HMAC-SHA256 signature for data integrity."""
    k = (key or settings.SECRET_KEY).encode("utf-8")
    return hmac.new(k, data.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_integrity(data: Any, expected_hash: str) -> bool:
    """Verify data integrity against expected SHA-256 hash."""
    return sha256_hash(data) == expected_hash
