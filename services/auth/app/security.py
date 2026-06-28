from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import secrets
import jwt
from app.config import settings

pwd_context = CryptContext(
    schemes=["sha256_crypt", "bcrypt_sha256", "bcrypt"],
    default="sha256_crypt",
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_secret(secret: str) -> str:
    return pwd_context.hash(secret)


def verify_secret(raw_secret: str, hashed_secret: str) -> bool:
    return pwd_context.verify(raw_secret, hashed_secret)


def generate_secret(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def create_otp_code(user_id: str, purpose: str, expire_minutes: int = 10) -> tuple[str, str]:
    code = str(secrets.randbelow(10**6)).zfill(6)
    hashed = hash_secret(code)
    return code, hashed


def verify_otp_code(raw_code: str, hashed_code: str) -> bool:
    return verify_secret(raw_code, hashed_code)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.InvalidTokenError:
        return None
