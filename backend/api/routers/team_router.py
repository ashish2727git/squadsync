"""
Team Management API Router
Endpoints for creating and managing teams.
"""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.team_schemas import (
    TeamCreateRequest,
    TeamResponse,
)
from backend.core.dependencies import get_db, get_current_user
from backend.models.models import Team, Organization, User

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
)
async def create_team(
    request: TeamCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TeamResponse:
    """Create a new team under an organization."""
    
    stmt = select(Organization).where(Organization.id == request.organization_id)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    new_team = Team(
        name=request.name,
        game_title=request.game_title,
        organization_id=request.organization_id,
        is_active=True,
    )
    
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    
    return TeamResponse(
        id=new_team.id,
        name=new_team.name,
        game_title=new_team.game_title,
        organization_id=new_team.organization_id,
        is_active=new_team.is_active,
        created_at=new_team.created_at,
    )


@router.get(
    "",
    response_model=List[TeamResponse],
    summary="List all teams",
)
async def list_teams(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    organization_id: Optional[UUID] = Query(None),
) -> List[TeamResponse]:
    """List all teams, optionally filtered by organization."""
    
    if organization_id:
        stmt = select(Team).where(
            and_(
                Team.organization_id == organization_id,
                Team.is_active == True,
            )
        )
    else:
        stmt = select(Team).where(Team.is_active == True)
    
    result = await db.execute(stmt)
    teams = result.scalars().all()
    
    return [
        TeamResponse(
            id=team.id,
            name=team.name,
            game_title=team.game_title,
            organization_id=team.organization_id,
            is_active=team.is_active,
            created_at=team.created_at,
        )
        for team in teams
    ]


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team details",
)
async def get_team(
    team_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TeamResponse:
    """Get detailed information about a team."""
    
    stmt = select(Team).where(Team.id == team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    return TeamResponse(
        id=team.id,
        name=team.name,
        game_title=team.game_title,
        organization_id=team.organization_id,
        is_active=team.is_active,
        created_at=team.created_at,
    )
