from __future__ import annotations
from typing import Annotated, List
from typing_extensions import Self
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column
from jose import jwt
from datetime import datetime
from pydantic import ValidationError

from src.logging.service import logger
from src.config import SHARED_SCHEMA_NAME
from src.config import JWT_SECRET_KEY
from src.auth import get_hashed_password, reuseable_oauth, ALGORITHM
from src.auth import TokenPayload

from src.models import AppModel, SharedModelMixin, IdentifierMixin
from src.validators import CreateValidator, ReadValidator

class Login(SharedModelMixin, IdentifierMixin, AppModel):
    hashed_password:    Mapped[str]         = mapped_column(nullable=False)
    verification_token: Mapped[uuid.uuid4]  = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    verified:           Mapped[bool]        = mapped_column(nullable=False, default=False)
    tenant_schema_name: Mapped[str]         = mapped_column(nullable=True)

    # Override this to handle the password => hashed_password conversion
    @classmethod
    async def create_one(
        cls,
        item: CreateValidator | Self,
        schema_name = SHARED_SCHEMA_NAME,
    ) -> List[int]:
        password = item.password
        del item.password
        item_dict = item.to_dict()
        item_dict['hashed_password'] = get_hashed_password(password)
        item_db = await super().create_one(item_dict, schema_name)
        return ReadValidator.model_construct(**item_db.to_dict())


async def get_unverified_login(token: Annotated[OAuth2PasswordBearer, Depends(reuseable_oauth)]) -> Login:
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            # TODO: Auto Renew?
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail='Token expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        login = await Login.read_by_identifier(
            identifier=token_data.sub,
            schema_name=SHARED_SCHEMA_NAME,
        )

        if login is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail='Login does not exist.',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return login

    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def get_current_login(
    token: Annotated[OAuth2PasswordBearer, Depends(reuseable_oauth)]
) -> Login:
    login = await get_unverified_login(token=token)
    if not login.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Login not verified. Please check email link and verify login first.',
        )
    return login
