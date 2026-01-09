"""
Squad Schedule API Router
FastAPI endpoints for squad events and daily goals.
"""

from datetime import datetime, timedelta
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.squad_schedule_schemas import (
    SquadDailyGoalCreateRequest,
    SquadDailyGoalDetail,
    SquadDailyGoalUpdateRequest,
    SquadEventCreateRequest,
    SquadEventDetail,
    SquadEventListResponse,
    SquadEventUpdateRequest,
    SquadScheduleDashboard,
)
from backend.core.permissions import can_access_squad
from backend.models.models import Squad, SquadDailyGoal, SquadEvent, User
from backend.services.squad_schedule_service import (
    EventNotFoundError,
    GoalNotFoundError,
    InvalidEventError,
    PermissionDeniedError,
    SquadNotFoundError,
    SquadScheduleService,
    SquadScheduleServiceError,
)

# Import dependencies from core module
from backend.core.dependencies import get_db, get_current_user


router = APIRouter(prefix="/api/v1/squads", tags=["squad-schedule"])


@router.post(
    "/{squad_id}/events",
    response_model=SquadEventDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create squad event",
    description="Create a new squad event. Only Squad Leaders and above can create events.",
)
async def create_event(
    squad_id: UUID,
    request: SquadEventCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadEventDetail:
    """
    Create a new squad event.

    Only Squad Leaders (or higher roles) can create events.
    """
    service = SquadScheduleService(db)

    try:
        event = await service.create_event(
            user=current_user,
            squad_id=squad_id,
            title=request.title,
            description=request.description,
            start_time=request.start_time,
            end_time=request.end_time,
            event_type=request.event_type,
            location=request.location,
            is_all_day=request.is_all_day,
            is_recurring=request.is_recurring,
            recurrence_pattern=request.recurrence_pattern,
            metadata=request.metadata,
        )

        await db.commit()

        return await _event_to_detail(db, event)

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
    except InvalidEventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except SquadScheduleServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{squad_id}/events",
    response_model=SquadEventListResponse,
    summary="Get squad events",
    description="Get events for a squad with optional date filtering.",
)
async def get_squad_events(
    squad_id: UUID,
    start_date: Optional[datetime] = Query(None, description="Filter events from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events until this date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> SquadEventListResponse:
    """
    Get events for a squad with efficient querying.

    Supports date filtering and pagination for dashboard loading.
    """
    service = SquadScheduleService(db)

    try:
        offset = (page - 1) * page_size
        events, total = await service.get_squad_events(
            squad_id=squad_id,
            user=current_user,
            start_date=start_date,
            end_date=end_date,
            limit=page_size,
            offset=offset,
        )

        event_details = []
        for event in events:
            detail = await _event_to_detail(db, event)
            event_details.append(detail)

        return SquadEventListResponse(
            events=event_details,
            total=total,
            page=page,
            page_size=page_size,
        )

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/{squad_id}/events/{event_id}",
    response_model=SquadEventDetail,
    summary="Get event by ID",
    description="Get detailed information about a specific event.",
)
async def get_event(
    squad_id: UUID,
    event_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadEventDetail:
    """
    Get event by ID.

    User must have access to the squad.
    """
    service = SquadScheduleService(db)

    try:
        event = await service.get_event(event_id, current_user)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found",
            )

        if event.squad_id != squad_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found in squad {squad_id}",
            )

        return await _event_to_detail(db, event)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.put(
    "/{squad_id}/events/{event_id}",
    response_model=SquadEventDetail,
    summary="Update squad event",
    description="Update a squad event. Only Squad Leaders and above can update events.",
)
async def update_event(
    squad_id: UUID,
    event_id: UUID,
    request: SquadEventUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadEventDetail:
    """
    Update a squad event.

    Only Squad Leaders (or higher roles) can update events.
    """
    service = SquadScheduleService(db)

    try:
        event = await service.update_event(
            user=current_user,
            event_id=event_id,
            title=request.title,
            description=request.description,
            start_time=request.start_time,
            end_time=request.end_time,
            event_type=request.event_type,
            location=request.location,
            is_all_day=request.is_all_day,
            is_recurring=request.is_recurring,
            recurrence_pattern=request.recurrence_pattern,
            metadata=request.metadata,
            is_active=request.is_active,
        )

        if event.squad_id != squad_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found in squad {squad_id}",
            )

        await db.commit()

        return await _event_to_detail(db, event)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidEventError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{squad_id}/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete squad event",
    description="Delete (deactivate) a squad event. Only Squad Leaders and above can delete events.",
)
async def delete_event(
    squad_id: UUID,
    event_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    Delete (deactivate) a squad event.

    Only Squad Leaders (or higher roles) can delete events.
    """
    service = SquadScheduleService(db)

    try:
        # Verify event belongs to squad
        event = await service.get_event(event_id, current_user)
        if not event or event.squad_id != squad_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found in squad {squad_id}",
            )

        await service.delete_event(current_user, event_id)
        await db.commit()

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{squad_id}/daily-goal",
    response_model=SquadDailyGoalDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create or update daily goal",
    description="Create or update squad daily goal. Only one active goal per squad. Only Squad Leaders can manage goals.",
)
async def create_or_update_daily_goal(
    squad_id: UUID,
    request: SquadDailyGoalCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadDailyGoalDetail:
    """
    Create or update squad daily goal.

    Only Squad Leaders (or higher roles) can create/update goals.
    Only one active goal per squad.
    """
    service = SquadScheduleService(db)

    try:
        goal = await service.create_or_update_daily_goal(
            user=current_user,
            squad_id=squad_id,
            goal_text=request.goal_text,
            target_date=request.target_date,
            metadata=request.metadata,
        )

        await db.commit()

        return await _goal_to_detail(db, goal)

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
    except SquadScheduleServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{squad_id}/daily-goal",
    response_model=SquadDailyGoalDetail,
    summary="Get squad daily goal",
    description="Get the current squad daily goal.",
)
async def get_daily_goal(
    squad_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadDailyGoalDetail:
    """
    Get squad daily goal.

    User must have access to the squad.
    """
    service = SquadScheduleService(db)

    try:
        goal = await service.get_daily_goal(squad_id, current_user)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Daily goal not found for squad {squad_id}",
            )

        return await _goal_to_detail(db, goal)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.patch(
    "/{squad_id}/daily-goal",
    response_model=SquadDailyGoalDetail,
    summary="Update daily goal",
    description="Update squad daily goal. Only Squad Leaders can update goals.",
)
async def update_daily_goal(
    squad_id: UUID,
    request: SquadDailyGoalUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SquadDailyGoalDetail:
    """
    Update squad daily goal.

    Only Squad Leaders (or higher roles) can update goals.
    """
    service = SquadScheduleService(db)

    try:
        goal = await service.update_daily_goal(
            user=current_user,
            squad_id=squad_id,
            goal_text=request.goal_text,
            is_completed=request.is_completed,
            metadata=request.metadata,
        )

        await db.commit()

        return await _goal_to_detail(db, goal)

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except GoalNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except SquadScheduleServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{squad_id}/schedule/dashboard",
    response_model=SquadScheduleDashboard,
    summary="Get squad schedule dashboard",
    description="Get optimized dashboard view with upcoming events and current daily goal. Efficient queries for fast loading.",
)
async def get_squad_dashboard(
    squad_id: UUID,
    upcoming_days: int = Query(7, ge=1, le=30, description="Number of days to look ahead for events"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> SquadScheduleDashboard:
    """
    Get squad schedule dashboard.

    Optimized for dashboard loading with minimal database hits.
    Returns upcoming events and current daily goal.
    """
    service = SquadScheduleService(db)

    try:
        dashboard_data = await service.get_squad_dashboard(
            squad_id=squad_id,
            user=current_user,
            upcoming_days=upcoming_days,
        )

        # Convert events to details
        event_details = []
        for event in dashboard_data["upcoming_events"]:
            detail = await _event_to_detail(db, event)
            event_details.append(detail)

        # Convert goal to detail
        goal_detail = None
        if dashboard_data["current_goal"]:
            goal_detail = await _goal_to_detail(db, dashboard_data["current_goal"])

        return SquadScheduleDashboard(
            squad_id=dashboard_data["squad_id"],
            squad_name=dashboard_data["squad_name"],
            upcoming_events=event_details,
            current_goal=goal_detail,
            event_count=dashboard_data["event_count"],
            goal_completion_rate=dashboard_data["goal_completion_rate"],
        )

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


async def _event_to_detail(db: AsyncSession, event: SquadEvent) -> SquadEventDetail:
    """Convert SquadEvent model to SquadEventDetail schema."""
    from sqlalchemy.orm import selectinload

    # Ensure relationships are loaded
    if not event.squad:
        await db.refresh(event, ["squad"])
    if not event.created_by:
        await db.refresh(event, ["created_by"])

    return SquadEventDetail(
        id=event.id,
        squad_id=event.squad_id,
        squad_name=event.squad.name,
        created_by_id=event.created_by_id,
        created_by_username=event.created_by.username if event.created_by else None,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        event_type=event.event_type,
        location=event.location,
        is_all_day=event.is_all_day,
        is_recurring=event.is_recurring,
        recurrence_pattern=event.recurrence_pattern,
        metadata=event.metadata,
        is_active=event.is_active,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


async def _goal_to_detail(db: AsyncSession, goal: SquadDailyGoal) -> SquadDailyGoalDetail:
    """Convert SquadDailyGoal model to SquadDailyGoalDetail schema."""
    # Ensure relationships are loaded
    if not goal.squad:
        await db.refresh(goal, ["squad"])
    if not goal.created_by:
        await db.refresh(goal, ["created_by"])
    if not goal.completed_by:
        await db.refresh(goal, ["completed_by"])

    return SquadDailyGoalDetail(
        id=goal.id,
        squad_id=goal.squad_id,
        squad_name=goal.squad.name,
        created_by_id=goal.created_by_id,
        created_by_username=goal.created_by.username if goal.created_by else None,
        goal_text=goal.goal_text,
        target_date=goal.target_date,
        is_completed=goal.is_completed,
        completed_at=goal.completed_at,
        completed_by_id=goal.completed_by_id,
        completed_by_username=goal.completed_by.username if goal.completed_by else None,
        metadata=goal.metadata,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )
