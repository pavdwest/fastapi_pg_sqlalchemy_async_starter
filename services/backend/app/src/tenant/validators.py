from typing import Optional
from datetime import datetime

from pydantic import (
    ConfigDict,
    Field,
    BaseModel
)

from src.validators import (
    ReadValidator,
    CreateValidator,
    UpdateValidator,
    UpdateWithIdValidator,
)
from src.utils import some_datetime, some_earlier_datetime


class TenantBase(BaseModel):
    identifier: str = Field(examples=['Important Bank 1', 'Cryptolord69420'])


model_config_base = ConfigDict(
    from_attributes=True,
    json_schema_extra={
        'example': {
            'identifier': 'Super Awesome Client Name',
        }
    }
)


class TenantCreate(CreateValidator, TenantBase):
    model_config = model_config_base


class TenantGet(ReadValidator, TenantBase):
    id:           int           = Field(examples=[127, 667])
    created_at:   datetime      = Field(title='Created At', description='UTC Timestamp of record creation', examples=[some_earlier_datetime, some_datetime])
    updated_at:   datetime      = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[some_earlier_datetime, some_datetime])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'identifier': 'Super Awesome Client Name',
                'created_at': some_earlier_datetime,
                'udpated_at': some_datetime,
            }
        }
    )


class TenantUpdateBase(BaseModel):
    identifier: Optional[str] = Field(examples=['Important Bank 1', 'Cryptolord69420'], default=None)


class TenantUpdate(UpdateValidator, TenantUpdateBase):
    pass


class TenantUpdateWithId(UpdateWithIdValidator, TenantUpdateBase):
    id:           int         = Field(examples=[127, 667])
