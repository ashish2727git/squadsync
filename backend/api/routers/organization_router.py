"""
Organization Management API Router
Endpoints for creating and managing organizations.
"""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.organization_schemas import (
    OrganizationCreateRequest,
    OrganizationResponse,
)
from backend.core.dependencies import get_db, get_current_user
from backend.models.models import Organization, User

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
)
async def create_organization(
    request: OrganizationCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationResponse:
    """Create a new organization."""
    
    new_org = Organization(
        name=request.name,
        description=request.description,
        is_active=True,
    )
    
    db.add(new_org)
    await db.commit()
    await db.refresh(new_org)
    
    return OrganizationResponse(
        id=new_org.id,
        name=new_org.name,
        description=new_org.description,
        is_active=new_org.is_active,
        created_at=new_org.created_at,
    )


@router.get(
    "",
    response_model=List[OrganizationResponse],
    summary="List all organizations",
)
async def list_organizations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[OrganizationResponse]:
    """List all active organizations."""
    
    stmt = select(Organization).where(Organization.is_active == True)
    result = await db.execute(stmt)
    orgs = result.scalars().all()
    
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            description=org.description,
            is_active=org.is_active,
            created_at=org.created_at,
        )
        for org in orgs
    ]


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Get organization details",
)
async def get_organization(
    organization_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OrganizationResponse:
    """Get detailed information about an organization."""
    
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        description=org.description,
        is_active=org.is_active,
        created_at=org.created_at,
    )
