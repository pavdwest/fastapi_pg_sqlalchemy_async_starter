# from datetime import datetime
# import uuid

# from pydantic import BaseModel

# from src.validators import (
#     AppModelGetValidator,
#     AppModelCreateValidator,
# )


# class LoginBase(BaseModel):
#     email:         str
#     name:          str = None
#     surname:       str = None


# class LoginCreate(AppModelCreateValidator, LoginCommon):
#     password: str
#     class Config:
#         from_attributes = True
#         populate_by_name = True

#         json_schema_extra = {
#             'example': {
#                 'email': 'joe.doe@incrediblecorruption.com',
#                 'password': '5up3rS3<uR3',
#                 'name': 'Joe',
#                 'surname': 'Doe',
#             }
#         }


# class LoginGet(AppModelGetValidator, LoginCommon):
#     # verification_token: uuid.UUID     # Send via email instead
#     verified: bool
#     class Config:
#         from_attributes = True
#         populate_by_name = True

#         json_schema_extra = {
#             'example': {
#                 'id': 27,
#                 'created_at': datetime.now(),
#                 'updated_at': datetime.now(),
#                 'email': 'joe.doe@incrediblecorruption.com',
#                 'verified': True,
#                 'name': 'Joe',
#                 'surname': 'Doe',
#             }
#         }


from typing import Optional
from datetime import datetime

from pydantic import ConfigDict, Field, BaseModel

from src.utils import some_datetime, some_earlier_datetime
from src.validators import (
    ReadValidator,
    CreateValidator,
    UpdateValidator,
    UpdateWithIdValidator,
)


class LoginBase(BaseModel):
    identifier:   str           = Field(description='email', examples=['jane.pain@company.com', 'joe@co.co.nl'])

model_config_base = ConfigDict(
    from_attributes=True,
    json_schema_extra={
        'example': {
            'identifier': 'joe.doe@incrediblecorruption.com',
        }
    }
)


class LoginCreate(CreateValidator, LoginBase):
    password: str          = Field(examples=['A Brief Horror Story of Time', 'The Book of Nod'])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'identifier': 'admin@pureformance.net',
                'password': 'admin',
            }
        }
    )


class LoginGet(ReadValidator, LoginBase):
    id:           int           = Field(examples=[127, 667])
    created_at:   datetime      = Field(title='Created At', description='UTC Timestamp of record creation', examples=[some_earlier_datetime, some_datetime])
    updated_at:   datetime      = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[some_earlier_datetime, some_datetime])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'identifier': 'joe.doe@incrediblecorruption.com',
                'created_at': some_earlier_datetime,
                'udpated_at': some_datetime,
            }
        }
    )


class LoginUpdateBase(BaseModel):
    identifier:   str           = Field(description='email', examples=['jane.pain@company.com', 'joe@co.co.nl'])

    model_config = model_config_base


class LoginUpdate(UpdateValidator, LoginUpdateBase):
    pass


class LoginUpdateWithId(UpdateWithIdValidator, LoginUpdateBase):
    id:           int           = Field(examples=[127, 667])
