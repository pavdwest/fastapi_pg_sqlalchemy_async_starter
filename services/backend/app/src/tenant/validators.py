from pydantic import BaseModel


class TenantCreate(BaseModel):
    identifier: str

    class Config:
        from_attributes = True
        populate_by_name = True

        json_schema_extra = {
            'example': {
                'identifier': 'Some Important Client',
            }
        }


class TenantGet(BaseModel):
    id: int
    identifier: str
    schema_name: str

    class Config:
        from_attributes = True
        populate_by_name = True

        json_schema_extra = {
            'example': {
                'id': 27,
                'schema_name': 'f0e7207e-5568-45ff-b877-74eb658649de',
                'identifier': 'Some Important Client',
            }
        }
