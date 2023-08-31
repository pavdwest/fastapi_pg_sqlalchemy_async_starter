from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from src.models import AppModel, IdentifierMixin, NameMixin


class Book(AppModel, IdentifierMixin, NameMixin):
    author: Mapped[str] = mapped_column()
    release_year: Mapped[Optional[int]] = mapped_column(nullable=True)
