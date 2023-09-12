from typing import Optional
from datetime import datetime, timedelta

from pydantic import ConfigDict, Field

from src.validators import AppValidator


class BookBase(AppValidator):
    identifier:   str           = Field(description='ISBN', examples=['978-0-618-68000-9', '978-3-16-148410-0'])
    name:         str           = Field(examples=['A Brief Horror Story of Time', 'The Book of Nod'])
    author:       str           = Field(examples=['Twisted Oliver', 'Bill Shakes Pierre'])
    release_year: Optional[int] = Field(title='Release Year', default=None, examples=[1994, 2023])


class BookCreate(BookBase):
    model_config = ConfigDict(
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


class BookGet(BookBase):
    id:           int           = Field(examples=[127, 667])
    created_at:   datetime      = Field(title='Created At', description='UTC Timestamp of record creation', examples=[datetime.now()])
    updated_at:   datetime      = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[datetime.now()])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'identifier': '978-3-16-148410-0',
                'name': 'A Brief Horror Story of Time',
                'author': 'Stephen Hawk King',
                'release_year': 2035,
                'created_at': datetime.utcnow() - timedelta(days=1),
                'udpated_at': datetime.utcnow(),
            }
        }
    )


class BookUpdate(AppValidator):
    identifier:   Optional[str] = Field(description='ISBN', examples=['978-0-618-68000-9', '978-3-16-148410-0'], default=None)
    name:         Optional[str] = Field(examples=['A Brief Horror Story of Time', 'The Book of Nod'], default=None)
    author:       Optional[str] = Field(examples=['Twisted Oliver', 'Bill Shakes Pierre'], default=None)
    release_year: Optional[int] = Field(title='Release Year', examples=[1994, 2023], default=None)


class BookUpdateWithPayload(AppValidator):
    id:           int           = Field(examples=[127, 667])
    identifier:   Optional[str] = Field(description='ISBN', examples=['978-0-618-68000-9', '978-3-16-148410-0'], default=None)
    name:         Optional[str] = Field(examples=['A Brief Horror Story of Time', 'The Book of Nod'], default=None)
    author:       Optional[str] = Field(examples=['Twisted Oliver', 'Bill Shakes Pierre'], default=None)
    release_year: Optional[int] = Field(title='Release Year', examples=[1994, 2023], default=None)
