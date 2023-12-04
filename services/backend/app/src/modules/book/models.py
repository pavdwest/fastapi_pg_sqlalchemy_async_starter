from typing import Optional
from typing_extensions import Self

from sqlalchemy.orm import Mapped, mapped_column

from src.models import AppModel, IdentifierMixin, NameMixin


class Book(AppModel, IdentifierMixin, NameMixin):
    author: Mapped[str] = mapped_column()
    release_year: Mapped[Optional[int]] = mapped_column(nullable=True)

    @classmethod
    async def get_mock_instance(cls, idx: int = None) -> Self:
        if idx is None:
            idx = await cls.get_max_id() + 1

        return cls(
            **{
            'identifier': f"id_{idx}",
            'name': f'Book: {idx}',
            'author': f'Author: {idx}',
            'release_year': idx % 1000 + 1000,
            }
        )
