from typing import Optional
from datetime import datetime, timedelta

from pydantic import ConfigDict, Field

from src.utils import some_datetime, some_earlier_datetime
from src.validators import AppValidator


class BookBase(AppValidator):
    identifier:   str           = Field(description='ISBN', examples=['978-0-618-68000-9', '978-3-16-148410-0'])
    name:         str           = Field(examples=['A Brief Horror Story of Time', 'The Book of Nod'])
    author:       str           = Field(examples=['Twisted Oliver', 'Bill Shakes Pierre'])
    release_year: Optional[int] = Field(title='Release Year', default=None, examples=[1994, 2023])


model_config_base = ConfigDict(
    from_attributes=True,
    json_schema_extra={
        'example': {
            'identifier': '978-3-16-148410-0',
            'name': 'A Brief Horror Story of Time',
            'author': 'Stephen Hawk King',
            'release_year': 2035,
        }
    }
)

class BookCreate(BookBase):
    model_config = model_config_base


class BookGet(BookBase):
    id:           int           = Field(examples=[127, 667])
    created_at:   datetime      = Field(title='Created At', description='UTC Timestamp of record creation', examples=[some_earlier_datetime, some_datetime])
    updated_at:   datetime      = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[some_earlier_datetime, some_datetime])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'identifier': '978-3-16-148410-0',
                'name': 'A Brief Horror Story of Time',
                'author': 'Stephen Hawk King',
                'release_year': 2035,
                'created_at': some_earlier_datetime,
                'udpated_at': some_datetime,
            }
        }
    )


class BookUpdate(AppValidator):
    identifier:   Optional[str] = Field(description='ISBN', examples=['978-0-618-68000-9', '978-3-16-148410-0'], default=None)
    name:         Optional[str] = Field(examples=['A Brief Horror Story of Time', 'The Book of Nod'], default=None)
    author:       Optional[str] = Field(examples=['Twisted Oliver', 'Bill Shakes Pierre'], default=None)
    release_year: Optional[int] = Field(title='Release Year', examples=[1994, 2023], default=None)

    model_config = model_config_base


class BookUpdateWithId(BookUpdate):
    id:           int           = Field(examples=[127, 667])
