from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from src.models import AppModel, NameMixin


class Reviewer(AppModel, NameMixin):
    username: Mapped[str] = mapped_column(unique=True)
    bio: Mapped[Optional[str]] = mapped_column()
