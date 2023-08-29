from pydantic import BaseModel


class BookCreate(BaseModel):
    identifier: str
    name: str
    author: str
    release_year: int

    class Config:
        from_attributes = True

        json_schema_extra = {
            'example': {
                'identifier': '978-3-16-148410-0',
                'name': 'A Brief Horror Story of Time',
                'author': 'Stephen Hawk King',
                'release_year': 2035,
            }
        }


class BookGet(BaseModel):
    identifier: str
    id: int
    name: str
    author: str
    release_year: int

    class Config:
        from_attributes = True

        json_schema_extra = {
            'example': {
                'id': 27,
                'identifier': '978-3-16-148410-0',
                'name': 'A Brief Horror Story of Time',
                'author': 'Stephen Hawk King',
                'release_year': 2035,
            }
        }
