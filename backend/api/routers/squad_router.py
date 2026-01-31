"""
Squad Management API Router
Endpoints for creating, joining, listing, and managing squads.
"""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.schemas.squad_schemas import (
    SquadCreateRequest,
    SquadResponse,
    SquadDetailResponse,
    SquadMemberResponse,
    SquadJoinRequest,
    QuickSquadCreateRequest,
)
from backend.core.dependencies import get_db, get_current_user
from backend.core.permissions import can_access_squad, can_manage_squad
from backend.models.models import (
    Squad,
    Team,
    Organization,
    User,
    squad_membership_table,
    SquadLeader,
)

router = APIRouter(prefix="/api/v1/squads", tags=["squads"])


@router.post(
    "/quick-create",
    response_model=SquadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Quick create squad (creates org, team, squad in one step)",
)
async def quick_create_squad(
    request: QuickSquadCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadResponse:
    """Quick create - creates organization, team, and squad in one step."""
    
    org = Organization(
        name=f"{current_user.username}'s Organization",
        description="Auto-created organization",
        is_active=True,
    )
    db.add(org)
    await db.flush()
    
    team = Team(
        name=f"{request.game_title} Team",
        description=f"Team for {request.game_title}",
        organization_id=org.id,
        is_active=True,
    )
    db.add(team)
    await db.flush()
    
    new_squad = Squad(
        name=request.squad_name,
        description=request.squad_description,
        team_id=team.id,
        max_members=request.max_members or 10,
        is_active=True,
    )
    db.add(new_squad)
    await db.flush()
    
    insert_stmt = squad_membership_table.insert().values(
        squad_id=new_squad.id,
        user_id=current_user.id,
        is_active=True,
    )
    await db.execute(insert_stmt)
    
    squad_leader = SquadLeader(
        squad_id=new_squad.id,
        user_id=current_user.id,
    )
    db.add(squad_leader)
    
    await db.commit()
    await db.refresh(new_squad)
    
    return SquadResponse(
        id=new_squad.id,
        name=new_squad.name,
        description=new_squad.description,
        team_id=new_squad.team_id,
        max_members=new_squad.max_members,
        member_count=1,
        is_active=new_squad.is_active,
        created_at=new_squad.created_at,
    )


@router.post(
    "",
    response_model=SquadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new squad",
)
async def create_squad(
    request: SquadCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadResponse:
    """Create a new squad under a team."""
    
    stmt = select(Team).where(Team.id == request.team_id)
    result = await db.execute(stmt)
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    new_squad = Squad(
        name=request.name,
        description=request.description,
        team_id=request.team_id,
        max_members=request.max_members or 10,
        is_active=True,
    )
    
    db.add(new_squad)
    await db.flush()
    
    insert_stmt = squad_membership_table.insert().values(
        squad_id=new_squad.id,
        user_id=current_user.id,
        is_active=True,
    )
    await db.execute(insert_stmt)
    
    squad_leader = SquadLeader(
        squad_id=new_squad.id,
        user_id=current_user.id,
    )
    db.add(squad_leader)
    
    await db.commit()
    await db.refresh(new_squad)
    
    return SquadResponse(
        id=new_squad.id,
        name=new_squad.name,
        description=new_squad.description,
        team_id=new_squad.team_id,
        max_members=new_squad.max_members,
        member_count=1,
        is_active=new_squad.is_active,
        created_at=new_squad.created_at,
    )


@router.get(
    "",
    response_model=List[SquadResponse],
    summary="List user's squads",
)
async def list_user_squads(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[SquadResponse]:
    """Get all squads the current user is a member of."""
    
    stmt = (
        select(Squad)
        .join(squad_membership_table, Squad.id == squad_membership_table.c.squad_id)
        .where(
            and_(
                squad_membership_table.c.user_id == current_user.id,
                squad_membership_table.c.is_active == True,
                Squad.is_active == True,
            )
        )
        .options(selectinload(Squad.members))
    )
    
    result = await db.execute(stmt)
    squads = result.scalars().all()
    
    squad_responses = []
    for squad in squads:
        member_count_stmt = select(func.count()).select_from(squad_membership_table).where(
            and_(
                squad_membership_table.c.squad_id == squad.id,
                squad_membership_table.c.is_active == True,
            )
        )
        member_count_result = await db.execute(member_count_stmt)
        member_count = member_count_result.scalar() or 0
        
        squad_responses.append(
            SquadResponse(
                id=squad.id,
                name=squad.name,
                description=squad.description,
                team_id=squad.team_id,
                max_members=squad.max_members,
                member_count=member_count,
                is_active=squad.is_active,
                created_at=squad.created_at,
            )
        )
    
    return squad_responses


@router.get(
    "/{squad_id}",
    response_model=SquadDetailResponse,
    summary="Get squad details",
)
async def get_squad(
    squad_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadDetailResponse:
    """Get detailed information about a squad."""
    
    if not await can_access_squad(db, current_user, squad_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this squad"
        )
    
    stmt = select(Squad).where(Squad.id == squad_id).options(selectinload(Squad.members))
    result = await db.execute(stmt)
    squad = result.scalar_one_or_none()
    
    if not squad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squad not found"
        )
    
    member_stmt = (
        select(User)
        .join(squad_membership_table, User.id == squad_membership_table.c.user_id)
        .where(
            and_(
                squad_membership_table.c.squad_id == squad_id,
                squad_membership_table.c.is_active == True,
            )
        )
    )
    member_result = await db.execute(member_stmt)
    members = member_result.scalars().all()
    
    leader_stmt = select(SquadLeader).where(SquadLeader.squad_id == squad_id)
    leader_result = await db.execute(leader_stmt)
    leaders = leader_result.scalars().all()
    leader_ids = {leader.user_id for leader in leaders}
    
    member_responses = [
        SquadMemberResponse(
            id=member.id,
            username=member.username,
            is_leader=member.id in leader_ids,
        )
        for member in members
    ]
    
    return SquadDetailResponse(
        id=squad.id,
        name=squad.name,
        description=squad.description,
        team_id=squad.team_id,
        max_members=squad.max_members,
        member_count=len(members),
        is_active=squad.is_active,
        created_at=squad.created_at,
        members=member_responses,
    )


@router.post(
    "/{squad_id}/join",
    status_code=status.HTTP_200_OK,
    summary="Join a squad",
)
async def join_squad(
    squad_id: UUID,
    request: SquadJoinRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Join an existing squad."""
    
    stmt = select(Squad).where(Squad.id == squad_id)
    result = await db.execute(stmt)
    squad = result.scalar_one_or_none()
    
    if not squad or not squad.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squad not found"
        )
    
    membership_check_stmt = select(squad_membership_table).where(
        and_(
            squad_membership_table.c.squad_id == squad_id,
            squad_membership_table.c.user_id == current_user.id,
        )
    )
    membership_check = await db.execute(membership_check_stmt)
    existing_membership = membership_check.first()
    
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this squad"
        )
    
    member_count_stmt = select(func.count()).select_from(squad_membership_table).where(
        and_(
            squad_membership_table.c.squad_id == squad_id,
            squad_membership_table.c.is_active == True,
        )
    )
    member_count_result = await db.execute(member_count_stmt)
    member_count = member_count_result.scalar() or 0
    
    if member_count >= squad.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Squad is full"
        )
    
    insert_stmt = squad_membership_table.insert().values(
        squad_id=squad_id,
        user_id=current_user.id,
        is_active=True,
    )
    await db.execute(insert_stmt)
    await db.commit()
    
    return {"message": "Successfully joined squad"}


@router.post(
    "/{squad_id}/leave",
    status_code=status.HTTP_200_OK,
    summary="Leave a squad",
)
async def leave_squad(
    squad_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Leave a squad."""
    
    if not await can_access_squad(db, current_user.id, squad_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this squad"
        )
    
    from sqlalchemy import update, delete
    
    update_stmt = (
        update(squad_membership_table)
        .where(
            and_(
                squad_membership_table.c.squad_id == squad_id,
                squad_membership_table.c.user_id == current_user.id,
            )
        )
        .values(is_active=False)
    )
    await db.execute(update_stmt)
    
    leader_delete_stmt = delete(SquadLeader).where(
        and_(
            SquadLeader.squad_id == squad_id,
            SquadLeader.user_id == current_user.id,
        )
    )
    await db.execute(leader_delete_stmt)
    
    await db.commit()
    
    return {"message": "Successfully left squad"}
