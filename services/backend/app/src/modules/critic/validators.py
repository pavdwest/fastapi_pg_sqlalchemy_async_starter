from typing import Optional
from datetime import datetime

from pydantic import ConfigDict, Field

from src.utils import some_datetime, some_earlier_datetime
from src.validators import AppValidator


class CriticBase(AppValidator):
    username: str           = Field(examples=['bookborn1', 'ultimate_worryer1983'])
    bio:      Optional[str] = Field(examples=['I like to read books.', 'I like to read books and write reviews.'], default=None)
    name:     Optional[str] = Field(examples=['John McBookface', 'Booker DeDimwitte'], default=None)


model_config_base = ConfigDict(
    from_attributes=True,
    json_schema_extra={
        'example': {
            'username': 'ultimate_worryer1983',
            'bio': 'I like to read books and write reviews.',
            'name': 'Booker DeDimwitte',
        }
    }
)


class CriticCreate(CriticBase):
    model_config = model_config_base


class CriticGet(CriticBase):
    id:         int      = Field(examples=[127, 667])
    created_at: datetime = Field(title='Created At', description='UTC Timestamp of record creation', examples=[some_earlier_datetime, some_datetime])
    updated_at: datetime = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[some_earlier_datetime, some_datetime])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'username': 'ultimate_worryer1983',
                'bio': 'I like to read books and write reviews.',
                'name': 'Booker DeDimwitte',
                'created_at': some_earlier_datetime,
                'udpated_at': some_datetime,
            }
        }
    )


class CriticUpdate(AppValidator):
    username: Optional[str] = Field(examples=['bookborn1', 'ultimate_worryer1983'], default=None)
    bio:      Optional[str] = Field(examples=['I like to read books.', 'I like to read books and write reviews.'], default=None)
    name:     Optional[str] = Field(examples=['John McBookface', 'Booker DeDimwitte'], default=None)

    model_config = model_config_base


class CriticUpdateWithId(CriticUpdate):
    id: int = Field(examples=[127, 667])
