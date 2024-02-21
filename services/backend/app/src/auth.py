from datetime import datetime
from venv import logger

from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any, Dict
from uuid import uuid4, UUID
# from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
# from pydantic import ValidationError

from src.config import JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from src.versions import ApiVersion


ALGORITHM = 'HS256'
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class TokenGet(BaseModel):
    access_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class TokenCreate(BaseModel):
    sub: str = None
    exp: datetime = None


def bearer_token_header(token: str) -> Dict:
    return {
        'Authorization': f"Bearer {token}"
    }

def get_hashed_password(password: str) -> str:
    # TODO: Why is this so slow?
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    logger.warning(password)
    logger.warning(hashed_pass)
    return password_context.verify(password, hashed_pass)


def get_random_token() -> UUID:
    """
    Utility method for random token.
    Not related to authentication flow really.

    Returns:
        str: Random token string
    """
    return uuid4()


def encode_item(item: Dict) -> str:
    """
    Encodes item in JWT

    Returns:
        str: Encoded JWT
    """
    return jwt.encode(item, JWT_SECRET_KEY, ALGORITHM)


def create_access_token(subject: Union[str, Any], expire_minutes: float = None) -> str:
    """
    Create access token for the Login.

    Args:
        subject (Union[str, Any]): Login data e.g. email address
        expire_minutes (float, optional): How long before token expires. Defaults ACCESS_TOKEN_EXPIRE_MINUTES if not provided.

    Returns:
        str: valid token
    """
    from src.logging.service import logger

    if expire_minutes is None:
        expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

    token_expires = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = TokenCreate(
        sub=str(subject),
        exp=token_expires
    )
    encoded_jwt = encode_item(to_encode.model_dump())
    return encoded_jwt


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl=f"{ApiVersion.V1}/login/get_access_token",
    scheme_name='JWT',
)
