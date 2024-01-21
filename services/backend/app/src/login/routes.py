# from typing import List, Dict

# from fastapi import APIRouter, status, HTTPException, Depends
# from fastapi import status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy import select
# from sqlalchemy.exc import IntegrityError
# from inflection import pluralize

# from src.auth import verify_password, create_access_token
# from src.auth import TokenGet
# from src.login.models import Login, get_unverified_login, get_current_login
# from src.login.validators import LoginCreate, LoginGet
# from src.database.service import DatabaseService


# Model = Login
# GetModelValidator = LoginGet
# CreateModelValidator = LoginCreate


# router = APIRouter(
#     tags=[Model.__tablename_friendly__],
#     prefix=f"/{Model.__tablename__}",
# )


# @router.post(
#     '/get_access_token',
#     summary="Get access token by login email and password",
#     response_model=TokenGet
# )
# async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     # Get login from form_data.username
#     q = select(Login).where(Login.email == form_data.username)
#     login: Login | None = (await db.execute_query(q)).scalar_one_or_none()

#     # If login email doesn't exist error out
#     if login is None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Incorrect email or password"
#         )
#     else:
#         # Note that login.password IS the HASHED password. We never stored the raw password.
#         if not verify_password(form_data.password, login.password):
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Incorrect email or password"
#             )

#         return TokenGet(
#             access_token=create_access_token(login.email),
#         )


# @router.post(
#     '/verify_login',
#     summary='Verify login details via token sent to email.',
#     response_model=Dict,
#     status_code=status.HTTP_200_OK,
#     description=f'Verity that the provided email actually exists and activate the login for further features.'
# )
# async def verify_login(
#     verification_token: str,
#     login: Login = Depends(get_unverified_login)
# ) -> Dict:
#     if verification_token == str(login.verification_token):
#         login.verified = True
#         await login.save()
#         return {
#             'message': 'Login details have been verified.'
#         }
#     else:
#         return {
#             'message': 'Incorrect verification token.'
#         }


# @router.get(
#     '/protected_unverified_route',
#     summary='Protected',
# )
# async def protected_unverified_route(
#     login: Login = Depends(get_unverified_login)
# ):
#     return {
#         'message': 'You have accessed the super secret route available only to logged-in users.'
#     }


# @router.get(
#     '/protected_verified_route',
#     summary='Protected',
# )
# async def protected_verified_route(
#     login: Login = Depends(get_current_login)
# ):
#     return {
#         'message': 'You have accessed the super secret route available only to verified users.'
#     }


# @router.post(
#     f"/create_one",
#     status_code=status.HTTP_200_OK,
#     summary=f"Create one {Model.__name__} in the database.",
#     description='Endpoint description. Will use the docstring if not provided.',
# )
# async def create_one(item: CreateModelValidator) -> GetModelValidator:
#     try:
#         db_item = await Model(**item.dict()).save()
#         return GetModelValidator.from_orm(db_item)
#     except IntegrityError as ex:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail='Email address is not available.',
#         )


# @router.get(
#     '/get_all',
#     status_code=status.HTTP_200_OK,
#     summary=f"Get all {pluralize(Model.__name__)} from the database.",
#     description='Endpoint description. Will use the docstring if not provided.',
# )
# async def get_all() -> List[GetModelValidator]:
#     res = await Model.fetch_all()
#     return [GetModelValidator.from_orm(i) for i in res]


from typing import Annotated, Dict
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from src.logging.service import logger
from src.versions import ApiVersion
from src.auth import get_hashed_password, verify_password, create_access_token, TokenGet
from src.login.models import Login, get_unverified_login, get_current_login
from src.login.validators import (
    LoginCreate,
    LoginGet,
    LoginUpdate,
    LoginUpdateWithId
)
from src.routes import generate_route_class


RouteClass = generate_route_class(
    ModelClass                 = Login,
    CreateValidatorClass       = LoginCreate,
    ReadValidatorClass         = LoginGet,
    UpdateValidatorClass       = LoginUpdate,
    UpdateWithIdValidatorClass = LoginUpdateWithId,
)
router_instance = RouteClass()
router: APIRouter = router_instance.router


wtf_router = APIRouter(
    tags=[Login.__tablename_friendly__],
    prefix=f"{ApiVersion.V1}/{Login.__tablename__}",
    redirect_slashes=False,
)

# # Gives a 422 WTF
# @(router_instance.router).get(
#     '/protected_verified_route',
#     summary='Protected',
#     description='Endpoint description. Will use the docstring if not provided.',
# )
# async def protected_verified_route(
#     login: Login = Depends(get_current_login)
# ) -> Dict:
#     return {
#         'message': f"Hi {login.identifier}, you have accessed the super secret route available only to logged-in users."
#     }

@wtf_router.post(
    '/signup',
    summary='Sign up.',
    response_model=LoginGet,
    status_code=status.HTTP_200_OK,
    description='Sign up for this service'
)
async def signup(
    item: LoginCreate
) -> LoginGet:
    hashed_password = get_hashed_password(item.password)
    del item.password
    item_db = await Login(**item.to_dict(), hashed_password=hashed_password).save()
    # TODO: Send email with auth code
    logger.warning(f"New User Verification Token: {item_db.verification_token}")
    return LoginGet.model_construct(**item_db.to_dict())


@wtf_router.post(
    '/verify_login',
    summary='Verify login details via token sent to email.',
    response_model=Dict,
    status_code=status.HTTP_200_OK,
    description='Verity that the provided email actually exists and activate the login for further features.'
)
async def verify_login(
    verification_token: str,
    login: Login = Depends(get_unverified_login)
) -> Dict:
    if verification_token == str(login.verification_token):
        login.verified = True
        await login.save()
        return {
            'message': 'Login details successfully verified.'
        }
    else:
        return {
            'message': 'Could not validate login. Please contact support.'
        }


@wtf_router.get(
    '/protected_unverified_route',
    summary='Protected',
)
async def protected_unverified_route(
    login: Login = Depends(get_unverified_login)
):
    return {
        'message': f"Hi {login.identifier}, you have accessed the super secret route available only to logged-in users."
    }


@wtf_router.get(
    '/protected_verified_route',
    summary='Protected',
)
async def protected_verified_route(
    login: Login = Depends(get_current_login)
):
    return {
        'message': f"Hi {login.identifier}, you have accessed the super secret route available only to verified logged-in users."
    }


# Endpoints
@wtf_router.post(
    '/get_access_token',
    summary="Get access token by login email and password",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Get login from form_data.username
    login = await Login.read_by_identifier(form_data.username)

    # If login email doesn't exist error out
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    else:
        # Note that we never stored the raw password.
        if not verify_password(form_data.password, login.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

        return TokenGet(
            access_token=create_access_token(login.identifier),
        )





# @router.get(
#     '/protected_verified_route',
#     summary='Protected',
# )
# async def protected_verified_route(
#     login: Login = Depends(get_current_login)
# ):
#     return {
#         'message': 'You have accessed the super secret route available only to verified users.'
#     }
