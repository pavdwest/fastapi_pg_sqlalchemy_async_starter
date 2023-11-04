from typing import Optional

from sqlalchemy import ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.models import AppModel, generate_unique_constraint
from src.modules.critic.models import Critic
from src.modules.book.models import Book


class Review(AppModel):
    title:     Mapped[str]           = mapped_column()
    critic_id: Mapped[int]           = mapped_column(BigInteger, ForeignKey(Critic.id))
    book_id:   Mapped[int]           = mapped_column(BigInteger, ForeignKey(Book.id))
    rating:    Mapped[int]           = mapped_column()
    body:      Mapped[Optional[str]] = mapped_column()

    __table_args__ = (
        generate_unique_constraint(
            'critic_id',
            'book_id',
            model_name='Review',
        ),
    )
