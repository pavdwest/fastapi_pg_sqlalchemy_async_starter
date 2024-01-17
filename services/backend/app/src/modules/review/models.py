from typing import Optional
from typing_extensions import Self

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from src.models import TenantModelMixin, AppModel, generate_unique_constraint
from src.modules.critic.models import Critic
from src.modules.book.models import Book


class Review(TenantModelMixin, AppModel):
    title:     Mapped[str]           = mapped_column()
    critic_id: Mapped[int]           = mapped_column(BigInteger, ForeignKey(Critic.id))
    # critic:    Mapped[Critic]        = relationship(back_populates='reviews')
    book_id:   Mapped[int]           = mapped_column(BigInteger, ForeignKey(Book.id))
    # book:      Mapped[Book]          = relationship(back_populates='reviews')
    rating:    Mapped[int]           = mapped_column()
    body:      Mapped[Optional[str]] = mapped_column()

    __table_args__ = (
        generate_unique_constraint(
            'critic_id',
            'book_id',
            model_name='Review',
        ),
    )

    @classmethod
    async def seed_one(cls) -> Self:
        idx = await cls.get_max_id() + 1
        return cls(
            title     = f'Review: {idx}',
            critic_id = (await Critic.seed_one()).id,
            book_id   = (await Book.seed_one()).id,
            rating    = idx % 5 + 1,
            body      = f'Lorem ipsum dolor sit amet, consectetur adipiscing elit book book good. {idx}',
        )
