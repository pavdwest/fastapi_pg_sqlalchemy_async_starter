import random
import datetime
from typing_extensions import Self

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from faker import Faker
from src.models import AppModel, TimestampMixin, IdentifierMixin


fake = Faker()

class Trade(AppModel, TimestampMixin, IdentifierMixin):
    instrument_id: Mapped[int] = mapped_column(BigInteger)
    mv: Mapped[float] = mapped_column()
    q: Mapped[float] = mapped_column()
    p: Mapped[float] = mapped_column()
    mv_local: Mapped[float] = mapped_column()
    q_local: Mapped[float] = mapped_column()
    p_local: Mapped[float] = mapped_column()

    @classmethod
    async def get_mock_instance(cls, idx: int = None) -> Self:
        if idx is None:
            idx = await cls.get_max_id() + 1

        return cls(
            **{
            'identifier': f"id_{idx}",
            'timestamp': fake.date_time_between(start_date=datetime.datetime.utcnow() - datetime.timedelta(days=3660), end_date=datetime.datetime.utcnow()),
            'instrument_id': random.randint(1, 100),
            'mv': random.randrange(-1000, 1000),
            'q': random.randrange(1000),
            'p': random.randrange(1000),
            'mv_local': random.randrange(-1000, 1000),
            'q_local': random.randrange(1000),
            'p_local': random.randrange(1000),
            }
        )
