"""
Role Assignment Router
Endpoints for managing user roles and permissions.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_current_user, get_db
from backend.core.permissions import can_access_organization, can_access_team
from backend.models.models import (
    OrganizationAdmin,
    SquadLeader,
    TeamManager,
    User,
)

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


class AssignOrgAdminRequest(BaseModel):
    user_id: UUID = Field(..., description="User to promote to Organization Admin")
    organization_id: UUID = Field(..., description="Organization ID")


class AssignTeamManagerRequest(BaseModel):
    user_id: UUID = Field(..., description="User to promote to Team Manager")
    team_id: UUID = Field(..., description="Team ID")


class AssignSquadLeaderRequest(BaseModel):
    user_id: UUID = Field(..., description="User to promote to Squad Leader")
    squad_id: UUID = Field(..., description="Squad ID")


class RoleResponse(BaseModel):
    success: bool
    message: str
    user_id: UUID
    role: str


@router.post("/assign-org-admin", response_model=RoleResponse)
async def assign_org_admin(
    request: AssignOrgAdminRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RoleResponse:
    """
    Assign Organization Admin role to a user.
    
    Requires: Current user must be an admin of the organization.
    """
    # Check if current user is org admin
    if not await can_access_organization(db, current_user, request.organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Organization Admins can assign this role"
        )
    
    # Check if target user exists
    target_user = await db.get(User, request.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already assigned
    existing_stmt = select(OrganizationAdmin).where(
        OrganizationAdmin.user_id == request.user_id,
        OrganizationAdmin.organization_id == request.organization_id
    )
    existing = await db.execute(existing_stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already an Organization Admin for this organization"
        )
    
    # Assign role
    org_admin = OrganizationAdmin(
        user_id=request.user_id,
        organization_id=request.organization_id
    )
    db.add(org_admin)
    await db.commit()
    
    return RoleResponse(
        success=True,
        message=f"User {target_user.username} assigned as Organization Admin",
        user_id=request.user_id,
        role="ORG_ADMIN"
    )


@router.post("/assign-team-manager", response_model=RoleResponse)
async def assign_team_manager(
    request: AssignTeamManagerRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RoleResponse:
    """
    Assign Team Manager role to a user.
    
    Requires: Current user must be an admin of the organization or manager of the team.
    """
    # Check if current user has access to this team
    if not await can_access_team(db, current_user, request.team_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Organization Admins or Team Managers can assign this role"
        )
    
    # Check if target user exists
    target_user = await db.get(User, request.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already assigned
    existing_stmt = select(TeamManager).where(
        TeamManager.user_id == request.user_id,
        TeamManager.team_id == request.team_id
    )
    existing = await db.execute(existing_stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a Team Manager for this team"
        )
    
    # Assign role
    team_manager = TeamManager(
        user_id=request.user_id,
        team_id=request.team_id
    )
    db.add(team_manager)
    await db.commit()
    
    return RoleResponse(
        success=True,
        message=f"User {target_user.username} assigned as Team Manager",
        user_id=request.user_id,
        role="TEAM_MANAGER"
    )


@router.post("/assign-squad-leader", response_model=RoleResponse)
async def assign_squad_leader(
    request: AssignSquadLeaderRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RoleResponse:
    """
    Assign Squad Leader role to a user.
    
    Requires: Current user must be org admin, team manager, or current squad leader.
    """
    from backend.core.permissions import can_manage_squad
    
    # Check if current user can manage this squad
    if not await can_manage_squad(db, current_user, request.squad_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Organization Admins, Team Managers, or Squad Leaders can assign this role"
        )
    
    # Check if target user exists
    target_user = await db.get(User, request.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already assigned
    existing_stmt = select(SquadLeader).where(
        SquadLeader.user_id == request.user_id,
        SquadLeader.squad_id == request.squad_id
    )
    existing = await db.execute(existing_stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a Squad Leader for this squad"
        )
    
    # Assign role
    squad_leader = SquadLeader(
        user_id=request.user_id,
        squad_id=request.squad_id
    )
    db.add(squad_leader)
    await db.commit()
    
    return RoleResponse(
        success=True,
        message=f"User {target_user.username} assigned as Squad Leader",
        user_id=request.user_id,
        role="SQUAD_LEADER"
    )


@router.delete("/remove-org-admin/{user_id}/{organization_id}", response_model=RoleResponse)
async def remove_org_admin(
    user_id: UUID,
    organization_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RoleResponse:
    """Remove Organization Admin role from a user."""
    if not await can_access_organization(db, current_user, organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Organization Admins can remove this role"
        )
    
    stmt = select(OrganizationAdmin).where(
        OrganizationAdmin.user_id == user_id,
        OrganizationAdmin.organization_id == organization_id
    )
    result = await db.execute(stmt)
    org_admin = result.scalar_one_or_none()
    
    if not org_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    await db.delete(org_admin)
    await db.commit()
    
    return RoleResponse(
        success=True,
        message="Organization Admin role removed",
        user_id=user_id,
        role="ORG_ADMIN_REMOVED"
    )


@router.delete("/remove-team-manager/{user_id}/{team_id}", response_model=RoleResponse)
async def remove_team_manager(
    user_id: UUID,
    team_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RoleResponse:
    """Remove Team Manager role from a user."""
    if not await can_access_team(db, current_user, team_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized users can remove this role"
        )
    
    stmt = select(TeamManager).where(
        TeamManager.user_id == user_id,
        TeamManager.team_id == team_id
    )
    result = await db.execute(stmt)
    team_manager = result.scalar_one_or_none()
    
    if not team_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    await db.delete(team_manager)
    await db.commit()
    
    return RoleResponse(
        success=True,
        message="Team Manager role removed",
        user_id=user_id,
        role="TEAM_MANAGER_REMOVED"
    )


@router.delete("/remove-squad-leader/{user_id}/{squad_id}", response_model=RoleResponse)
async def remove_squad_leader(
    user_id: UUID,
    squad_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RoleResponse:
    """Remove Squad Leader role from a user."""
    from backend.core.permissions import can_manage_squad
    
    if not await can_manage_squad(db, current_user, squad_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized users can remove this role"
        )
    
    stmt = select(SquadLeader).where(
        SquadLeader.user_id == user_id,
        SquadLeader.squad_id == squad_id
    )
    result = await db.execute(stmt)
    squad_leader = result.scalar_one_or_none()
    
    if not squad_leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    await db.delete(squad_leader)
    await db.commit()
    
    return RoleResponse(
        success=True,
        message="Squad Leader role removed",
        user_id=user_id,
        role="SQUAD_LEADER_REMOVED"
    )
