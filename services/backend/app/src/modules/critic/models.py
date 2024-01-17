from typing import Optional
from typing_extensions import Self

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from src.database.service import DatabaseService
from src.models import TenantModelMixin, AppModel, NameMixin


class Critic(TenantModelMixin, AppModel, NameMixin):
    username: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[Optional[str]] = mapped_column()

    @classmethod
    async def get_by_username(cls, username: str) -> Self:
        async with DatabaseService.async_session() as session:
            q = select(cls.get_model_class()).where(cls.get_model_class().username == username)
            res = await session.execute(q)
            return res.scalars().first()
