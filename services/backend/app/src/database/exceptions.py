from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions._base import UnknownPostgresError
from asyncpg.exceptions import (
    PostgresError,
    UniqueViolationError,
    ForeignKeyViolationError,
)
from fastapi import HTTPException, status


# If original exception has valid pgcode return that class, otherwise UnkownPostgresError
def ExceptionProxy(e: IntegrityError) -> Exception:
    klass = PostgresError.get_message_class_for_sqlstate(e.orig.pgcode)
    return e.__class__ if klass == UnknownPostgresError else klass


# Alternative version of the above that raises the exception
def raise_known(e: IntegrityError) -> None:
    klass = PostgresError.get_message_class_for_sqlstate(e.orig.pgcode)

    # Switch to raise specific exception class
    if klass == UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e.orig.__context__)
        )
    elif klass == ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e.orig.__context__),
        )
    else:
        raise e
