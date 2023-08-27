from pydantic import BaseModel


class BookCreate(BaseModel):
    name: str
    author: str
    release_year: int

    class Config:
        orm_mode = True
        from_attributes = True

        json_schema_extra = {
            'example': {
                'name': 'A Brief Horror Story of Time',
                'author': 'Stephen Hawk King',
                'release_year': 2035,
            }
        }


class BookGet(BaseModel):
    id: int
    name: str
    author: str
    release_year: int

    class Config:
        orm_mode = True
        from_attributes = True

        json_schema_extra = {
            'example': {
                'id': 27,
                'name': 'A Brief Horror Story of Time',
                'author': 'Stephen Hawk King',
                'release_year': 2035,
            }
        }
