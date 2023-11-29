from typing import Optional
from datetime import datetime

from pydantic import ConfigDict, Field, BaseModel

from src.utils import some_datetime, some_earlier_datetime
from src.validators import (
    AppValidator,
    GetValidator,
    CreateValidator,
    UpdateValidator,
    UpdateWithIdValidator,
)


class ReviewBase(BaseModel):
    title:     str = Field(examples=['Review: With a View', 'A Review to Admire'])
    critic_id: int = Field(examples=[1, 27])
    book_id:   int = Field(examples=[1, 27])
    rating:    int = Field(examples=[1, 5], ge=1, le=5)
    body:      str = Field(examples=['This book was great!', 'This book was terrible!'])


model_config_base = ConfigDict(
    from_attributes=True,
    json_schema_extra={
        'example': {
            'title': 'Review: With a View',
            'critic_id': 1,
            'book_id': 27,
            'rating': 4,
            'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit book book good.'
        }
    }
)


class ReviewCreate(CreateValidator, ReviewBase):
    model_config = model_config_base


class ReviewGet(GetValidator, ReviewBase):
    id:         int      = Field(examples=[127, 667])
    created_at: datetime = Field(title='Created At', description='UTC Timestamp of record creation', examples=[some_earlier_datetime, some_datetime])
    updated_at: datetime = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[some_earlier_datetime, some_datetime])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'title': 'Review: With a View',
                'critic_id': 1,
                'book_id': 27,
                'rating': 4,
                'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit book book good.',
                'created_at': some_earlier_datetime,
                'udpated_at': some_datetime,
            }
        }
    )


class ReviewUpdateBase(BaseModel):
    title:     Optional[str] = Field(examples=['Review: With a View', 'A Review to Admire'])
    critic_id: Optional[int] = Field(examples=[1, 27])
    book_id:   Optional[int] = Field(examples=[1, 27])
    rating:    Optional[int] = Field(examples=[1, 5], ge=1, le=5)
    body:      Optional[str] = Field(examples=['This book was great!', 'This book was terrible!'])

    model_config = model_config_base


class ReviewUpdate(UpdateValidator, ReviewUpdateBase):
    pass


class ReviewUpdateWithId(UpdateWithIdValidator, ReviewUpdateBase):
    id:        int           = Field(examples=[1, 27])
