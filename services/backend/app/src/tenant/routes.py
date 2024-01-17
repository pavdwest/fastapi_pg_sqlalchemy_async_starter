from typing import List

from fastapi import APIRouter, status

from src.tenant.models import Tenant
from src.tenant.validators import TenantCreate, TenantGet


model_class = Tenant


router = APIRouter(
    tags=[model_class.__tablename_friendly__],
    prefix=f"/{model_class.__tablename__}",
)


@router.post(
    f"/create_one",
    status_code=status.HTTP_200_OK,
    summary=f"Create one {model_class.__name__} in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def create_one(item: TenantCreate) -> TenantGet:
    tenant: Tenant = await Tenant(**item.model_dump()).create()
    await tenant.provision()
    return TenantGet.from_orm(tenant)


@router.get(
    f"/get_all",
    response_model=List[TenantGet],
    status_code=status.HTTP_200_OK,
    summary=f"Get all instances of {model_class.__name__} stored in the database.",
    description='Endpoint description. Will use the docstring if not provided.',
)
async def get_all() -> List[TenantGet]:
    items = await Tenant.fetch_all()
    print(items)
    return [TenantGet.from_orm(item) for item in items]
