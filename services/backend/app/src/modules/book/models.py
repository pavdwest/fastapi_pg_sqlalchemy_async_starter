from sqlalchemy import Column, Integer, String

from src.models import AppModel


class Book(AppModel):
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
