"""
Summon API Router
FastAPI endpoints for summon creation, management, and responses.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.summon_schemas import (
    SummonCreateRequest,
    SummonDetail,
    SummonListResponse,
    SummonResponseDetail,
    SummonResponseUpdateRequest,
)
from backend.core.permissions import can_access_squad
from backend.models.models import ResponseType, Summon, SummonResponse, User
from backend.services.summon_service import (
    InvalidSummonStateError,
    PermissionDeniedError,
    SquadNotFoundError,
    SummonNotFoundError,
    SummonService,
    SummonServiceError,
)

# Import dependencies from core module
from backend.core.dependencies import get_db, get_current_user


router = APIRouter(prefix="/api/v1/summons", tags=["summons"])


@router.post(
    "/",
    response_model=SummonDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new summon",
    description="Create a new summon for a squad. Only Squad Leaders and above can create summons.",
)
async def create_summon(
    request: SummonCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SummonDetail:
    """
    Create a new summon for a squad.

    Only Squad Leaders (or higher roles) can create summons.
    Creates SummonResponse records for all active squad members with PENDING status.
    Publishes realtime notifications via Redis.
    """
    service = SummonService(db)

    try:
        summon = await service.create_summon(
            user=current_user,
            squad_id=request.squad_id,
            title=request.title,
            description=request.description,
            expires_at=request.expires_at,
        )

        await db.commit()

        # Convert to response model
        return await _summon_to_detail(db, summon, current_user)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except SquadNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except SummonServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{summon_id}",
    response_model=SummonDetail,
    summary="Get summon by ID",
    description="Get detailed information about a specific summon.",
)
async def get_summon(
    summon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SummonDetail:
    """
    Get summon by ID with all responses.

    User must have access to the squad that owns the summon.
    """
    service = SummonService(db)

    try:
        summon = await service.get_summon_by_id(summon_id, current_user)
        if not summon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Summon {summon_id} not found",
            )

        return await _summon_to_detail(db, summon, current_user)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/{summon_id}/respond",
    response_model=SummonResponseDetail,
    summary="Respond to a summon",
    description="Submit or update your response to a summon. Members can ACCEPT, DECLINE, or MAYBE.",
)
async def respond_to_summon(
    summon_id: UUID,
    request: SummonResponseUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SummonResponseDetail:
    """
    Submit or update response to a summon.

    Squad members can respond with ACCEPT, DECLINE, or MAYBE.
    Publishes realtime notification to summon creator and squad channel.
    """
    service = SummonService(db)

    try:
        response = await service.update_summon_response(
            user=current_user,
            summon_id=summon_id,
            response_type=request.response_type,
            message=request.message,
        )

        await db.commit()

        # Reload with user relationship
        await db.refresh(response)
        await db.refresh(response.user)

        return SummonResponseDetail(
            id=response.id,
            summon_id=response.summon_id,
            user_id=response.user_id,
            username=response.user.username,
            response_type=response.response_type,
            message=response.message,
            created_at=response.created_at,
        )

    except SummonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except InvalidSummonStateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{summon_id}/responses",
    response_model=list[SummonResponseDetail],
    summary="Get all responses for a summon",
    description="Get all responses for a summon. Only accessible to squad members and above.",
)
async def get_summon_responses(
    summon_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[SummonResponseDetail]:
    """
    Get all responses for a summon.

    Returns list of all member responses with user information.
    """
    service = SummonService(db)

    try:
        responses = await service.get_summon_responses(summon_id, current_user)

        return [
            SummonResponseDetail(
                id=response.id,
                summon_id=response.summon_id,
                user_id=response.user_id,
                username=response.user.username,
                response_type=response.response_type,
                message=response.message,
                created_at=response.created_at,
            )
            for response in responses
        ]

    except SummonNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/squad/{squad_id}",
    response_model=SummonListResponse,
    summary="Get all summons for a squad",
    description="Get all summons for a specific squad. Requires squad access permissions.",
)
async def get_squad_summons(
    squad_id: UUID,
    page: int = 1,
    page_size: int = 20,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SummonListResponse:
    """
    Get all summons for a squad with pagination.

    User must have access to the squad.
    """
    # Check permissions
    can_access = await can_access_squad(db, current_user, squad_id)
    if not can_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {current_user.id} does not have access to squad {squad_id}",
        )

    # Get total count
    count_stmt = select(func.count(Summon.id)).where(Summon.squad_id == squad_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Get paginated summons
    stmt = (
        select(Summon)
        .where(Summon.squad_id == squad_id)
        .order_by(Summon.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    summons = result.scalars().all()

    # Convert to detail models
    summon_details = []
    for summon in summons:
        detail = await _summon_to_detail(db, summon, current_user)
        summon_details.append(detail)

    return SummonListResponse(
        summons=summon_details,
        total=total,
        page=page,
        page_size=page_size,
    )


async def _summon_to_detail(
    db: AsyncSession,
    summon: Summon,
    current_user: User,
) -> SummonDetail:
    """
    Convert Summon model to SummonDetail schema.

    Helper function to build response model with all relationships.
    """
    # Ensure relationships are loaded
    if not summon.squad:
        await db.refresh(summon, ["squad"])
    if not summon.created_by:
        await db.refresh(summon, ["created_by"])
    if not summon.responses:
        await db.refresh(summon, ["responses"])

    # Get response counts
    counts_stmt = (
        select(
            SummonResponse.response_type,
            func.count(SummonResponse.id).label("count"),
        )
        .where(SummonResponse.summon_id == summon.id)
        .group_by(SummonResponse.response_type)
    )
    counts_result = await db.execute(counts_stmt)
    response_counts = {
        row[0].value: row[1] for row in counts_result.all()
    }

    # Ensure all response types are represented
    response_summary = {
        "PENDING": response_counts.get(ResponseType.PENDING.value, 0),
        "ACCEPT": response_counts.get(ResponseType.ACCEPT.value, 0),
        "DECLINE": response_counts.get(ResponseType.DECLINE.value, 0),
        "MAYBE": response_counts.get(ResponseType.MAYBE.value, 0),
    }

    # Get total member count from squad
    from backend.models.models import squad_membership_table

    member_count_stmt = (
        select(func.count(squad_membership_table.c.user_id))
        .where(
            and_(
                squad_membership_table.c.squad_id == summon.squad_id,
                squad_membership_table.c.is_active == True,
            )
        )
    )
    member_count_result = await db.execute(member_count_stmt)
    total_members = member_count_result.scalar_one()

    # Build response details
    response_details = []
    for response in summon.responses:
        if not response.user:
            await db.refresh(response, ["user"])
        response_details.append(
            SummonResponseDetail(
                id=response.id,
                summon_id=response.summon_id,
                user_id=response.user_id,
                username=response.user.username,
                response_type=response.response_type,
                message=response.message,
                created_at=response.created_at,
            )
        )

    return SummonDetail(
        id=summon.id,
        squad_id=summon.squad_id,
        squad_name=summon.squad.name,
        created_by_id=summon.created_by_id,
        created_by_username=summon.created_by.username if summon.created_by else "Unknown",
        title=summon.title,
        description=summon.description,
        status=summon.status,
        expires_at=summon.expires_at,
        created_at=summon.created_at,
        total_members=total_members,
        responses=response_details,
        response_summary=response_summary,
    )
