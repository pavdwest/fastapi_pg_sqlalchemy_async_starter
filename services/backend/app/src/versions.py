from enum import Enum


class ApiVersion(str, Enum):
    NONE: str = ''
    V1: str = '/api/v1'
