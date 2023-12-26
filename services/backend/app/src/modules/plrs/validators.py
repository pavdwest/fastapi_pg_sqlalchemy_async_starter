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


class TradeBase(BaseModel):
    identifier:   str    = Field(description='Some unique reference', examples=['978-0-618-68000-9', '978-3-16-148410-0'])
    instrument_id: float = Field(float)
    timestamp: datetime  = Field(datetime)
    mv: float            = Field(float)
    q: float             = Field(float)
    p: float             = Field(float)
    mv_local: float      = Field(float)
    q_local: float       = Field(float)
    p_local: float       = Field(float)


model_config_base = ConfigDict(
    from_attributes=True,
    json_schema_extra={
        'example': {
            'identifier': 'transaction_666',
            'timestamp': datetime.utcnow(),
            'instrument_id': 666,
            'mv': 666.66,
            'q': 666.66,
            'p': 666.66,
            'mv_local': 666.66,
            'q_local': 666.66,
            'p_local': 666.66,
        }
    }
)


class TradeCreate(CreateValidator, TradeBase):
    model_config = model_config_base


class TradeGet(ReadValidator, TradeBase):
    id:           int           = Field(examples=[127, 667])
    created_at:   datetime      = Field(title='Created At', description='UTC Timestamp of record creation', examples=[some_earlier_datetime, some_datetime])
    updated_at:   datetime      = Field(title='Updated At', description='The last time this record was updated (UTC)', examples=[some_earlier_datetime, some_datetime])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 27,
                'identifier': 'transaction_666',
                'timestamp': datetime.utcnow(),
                'instrument_id': 666,
                'mv': 666.66,
                'q': 666.66,
                'p': 666.66,
                'mv_local': 666.66,
                'q_local': 666.66,
                'p_local': 666.66,
                'created_at': some_earlier_datetime,
                'udpated_at': some_datetime,
            }
        }
    )


class TradeUpdateBase(BaseModel):
    identifier: Optional[str]     = Field(str)
    instrument_id: Optional[int]  = Field(int)
    timestamp: Optional[datetime] = Field(datetime)
    mv: Optional[float]           = Field(float)
    q: Optional[float]            = Field(float)
    p: Optional[float]            = Field(float)
    mv_local: Optional[float]     = Field(float)
    q_local: Optional[float]      = Field(float)
    p_local: Optional[float]      = Field(float)

    model_config = model_config_base


class TradeUpdate(UpdateValidator, TradeUpdateBase):
    pass


class TradeUpdateWithId(UpdateWithIdValidator, TradeUpdateBase):
    id:           int           = Field(examples=[127, 667])
