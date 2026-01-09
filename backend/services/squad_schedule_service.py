"""
Squad Schedule Service
Business logic for squad events and daily goals.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.permissions import can_manage_squad, can_access_squad
from backend.models.models import Squad, SquadDailyGoal, SquadEvent, User


class SquadScheduleServiceError(Exception):
    """Base exception for squad schedule service errors."""

    pass


class PermissionDeniedError(SquadScheduleServiceError):
    """Raised when user lacks required permissions."""

    pass


class SquadNotFoundError(SquadScheduleServiceError):
    """Raised when squad is not found."""

    pass


class EventNotFoundError(SquadScheduleServiceError):
    """Raised when event is not found."""

    pass


class GoalNotFoundError(SquadScheduleServiceError):
    """Raised when daily goal is not found."""

    pass


class InvalidEventError(SquadScheduleServiceError):
    """Raised when event data is invalid."""

    pass


class SquadScheduleService:
    """Service for managing squad events and daily goals."""

    def __init__(self, db: AsyncSession):
        """
        Initialize squad schedule service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_event(
        self,
        user: User,
        squad_id: UUID,
        title: str,
        start_time: datetime,
        description: Optional[str] = None,
        end_time: Optional[datetime] = None,
        event_type: str = "general",
        location: Optional[str] = None,
        is_all_day: bool = False,
        is_recurring: bool = False,
        recurrence_pattern: Optional[str] = None,
        metadata: dict = None,
    ) -> SquadEvent:
        """
        Create a new squad event.

        Only Squad Leaders (or higher roles) can create events.

        Args:
            user: User creating the event
            squad_id: UUID of the squad
            title: Event title
            start_time: Event start time
            description: Optional event description
            end_time: Optional event end time
            event_type: Event type (practice, match, meeting, general)
            location: Optional event location
            is_all_day: Whether event is all-day
            is_recurring: Whether event is recurring
            recurrence_pattern: Recurrence pattern (daily, weekly, monthly)
            metadata: Additional metadata for analytics

        Returns:
            Created SquadEvent object

        Raises:
            PermissionDeniedError: If user cannot manage the squad
            SquadNotFoundError: If squad doesn't exist
        """
        # Check permissions - only squad leaders and above can create events
        can_manage = await can_manage_squad(self.db, user, squad_id)
        if not can_manage:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to create events for squad {squad_id}"
            )

        # Verify squad exists
        squad_stmt = select(Squad).where(and_(Squad.id == squad_id, Squad.is_active == True))
        result = await self.db.execute(squad_stmt)
        squad = result.scalar_one_or_none()

        if not squad:
            raise SquadNotFoundError(f"Squad {squad_id} not found or inactive")

        # Create event
        event = SquadEvent(
            squad_id=squad_id,
            created_by_id=user.id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            event_type=event_type,
            location=location,
            is_all_day=is_all_day,
            is_recurring=is_recurring,
            recurrence_pattern=recurrence_pattern,
            metadata=metadata or {},
        )
        self.db.add(event)
        await self.db.flush()

        return event

    async def update_event(
        self,
        user: User,
        event_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        location: Optional[str] = None,
        is_all_day: Optional[bool] = None,
        is_recurring: Optional[bool] = None,
        recurrence_pattern: Optional[str] = None,
        metadata: Optional[dict] = None,
        is_active: Optional[bool] = None,
    ) -> SquadEvent:
        """
        Update a squad event.

        Only Squad Leaders (or higher roles) can update events.

        Args:
            user: User updating the event
            event_id: UUID of the event
            title: Optional new title
            description: Optional new description
            start_time: Optional new start time
            end_time: Optional new end time
            event_type: Optional new event type
            location: Optional new location
            is_all_day: Optional all-day flag
            is_recurring: Optional recurring flag
            recurrence_pattern: Optional recurrence pattern
            metadata: Optional metadata update
            is_active: Optional active flag

        Returns:
            Updated SquadEvent object

        Raises:
            PermissionDeniedError: If user cannot manage the squad
            EventNotFoundError: If event doesn't exist
        """
        # Get event with squad relationship
        stmt = (
            select(SquadEvent)
            .options(selectinload(SquadEvent.squad))
            .where(SquadEvent.id == event_id)
        )
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        # Check permissions
        can_manage = await can_manage_squad(self.db, user, event.squad_id)
        if not can_manage:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to update event {event_id}"
            )

        # Update fields
        if title is not None:
            event.title = title
        if description is not None:
            event.description = description
        if start_time is not None:
            event.start_time = start_time
        if end_time is not None:
            event.end_time = end_time
        if event_type is not None:
            event.event_type = event_type
        if location is not None:
            event.location = location
        if is_all_day is not None:
            event.is_all_day = is_all_day
        if is_recurring is not None:
            event.is_recurring = is_recurring
        if recurrence_pattern is not None:
            event.recurrence_pattern = recurrence_pattern
        if metadata is not None:
            # Merge metadata
            event.metadata = {**event.metadata, **metadata}
        if is_active is not None:
            event.is_active = is_active

        event.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        return event

    async def get_event(self, event_id: UUID, user: User) -> Optional[SquadEvent]:
        """
        Get event by ID with permission check.

        Args:
            event_id: UUID of the event
            user: User requesting the event

        Returns:
            SquadEvent object if found and user has access, None otherwise

        Raises:
            PermissionDeniedError: If user cannot access the squad
        """
        stmt = (
            select(SquadEvent)
            .options(selectinload(SquadEvent.squad), selectinload(SquadEvent.created_by))
            .where(SquadEvent.id == event_id)
        )
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            return None

        # Check if user can access the squad
        can_access = await can_access_squad(self.db, user, event.squad_id)
        if not can_access:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to view event {event_id}"
            )

        return event

    async def get_squad_events(
        self,
        squad_id: UUID,
        user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[SquadEvent], int]:
        """
        Get events for a squad with efficient querying.

        Args:
            squad_id: UUID of the squad
            user: User requesting events
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of events to return
            offset: Offset for pagination

        Returns:
            Tuple of (list of events, total count)

        Raises:
            PermissionDeniedError: If user cannot access the squad
        """
        # Check permissions
        can_access = await can_access_squad(self.db, user, squad_id)
        if not can_access:
            raise PermissionDeniedError(
                f"User {user.id} does not have access to squad {squad_id}"
            )

        # Build query
        conditions = [
            SquadEvent.squad_id == squad_id,
            SquadEvent.is_active == True,
        ]

        if start_date:
            conditions.append(SquadEvent.start_time >= start_date)
        if end_date:
            conditions.append(SquadEvent.start_time <= end_date)

        # Get total count (efficient for dashboard)
        count_stmt = select(func.count(SquadEvent.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Get events with efficient loading
        stmt = (
            select(SquadEvent)
            .options(selectinload(SquadEvent.squad), selectinload(SquadEvent.created_by))
            .where(and_(*conditions))
            .order_by(SquadEvent.start_time.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return list(events), total

    async def delete_event(self, user: User, event_id: UUID) -> None:
        """
        Delete (deactivate) a squad event.

        Only Squad Leaders (or higher roles) can delete events.

        Args:
            user: User deleting the event
            event_id: UUID of the event

        Raises:
            PermissionDeniedError: If user cannot manage the squad
            EventNotFoundError: If event doesn't exist
        """
        # Get event
        stmt = (
            select(SquadEvent)
            .options(selectinload(SquadEvent.squad))
            .where(SquadEvent.id == event_id)
        )
        result = await self.db.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        # Check permissions
        can_manage = await can_manage_squad(self.db, user, event.squad_id)
        if not can_manage:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to delete event {event_id}"
            )

        # Soft delete (deactivate)
        event.is_active = False
        event.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def create_or_update_daily_goal(
        self,
        user: User,
        squad_id: UUID,
        goal_text: str,
        target_date: datetime,
        metadata: dict = None,
    ) -> SquadDailyGoal:
        """
        Create or update squad daily goal.

        Only one active goal per squad. Only Squad Leaders can create/update.

        Args:
            user: User creating/updating the goal
            squad_id: UUID of the squad
            goal_text: Goal text
            target_date: Date this goal is for
            metadata: Additional metadata for analytics

        Returns:
            Created or updated SquadDailyGoal object

        Raises:
            PermissionDeniedError: If user cannot manage the squad
            SquadNotFoundError: If squad doesn't exist
        """
        # Check permissions
        can_manage = await can_manage_squad(self.db, user, squad_id)
        if not can_manage:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to manage goals for squad {squad_id}"
            )

        # Verify squad exists
        squad_stmt = select(Squad).where(and_(Squad.id == squad_id, Squad.is_active == True))
        result = await self.db.execute(squad_stmt)
        squad = result.scalar_one_or_none()

        if not squad:
            raise SquadNotFoundError(f"Squad {squad_id} not found or inactive")

        # Get existing goal (unique constraint ensures one per squad)
        goal_stmt = select(SquadDailyGoal).where(SquadDailyGoal.squad_id == squad_id)
        goal_result = await self.db.execute(goal_stmt)
        goal = goal_result.scalar_one_or_none()

        if goal:
            # Update existing goal
            goal.goal_text = goal_text
            goal.target_date = target_date
            if metadata:
                goal.metadata = {**goal.metadata, **metadata}
            goal.updated_at = datetime.now(timezone.utc)
        else:
            # Create new goal
            goal = SquadDailyGoal(
                squad_id=squad_id,
                created_by_id=user.id,
                goal_text=goal_text,
                target_date=target_date,
                metadata=metadata or {},
            )
            self.db.add(goal)

        await self.db.flush()
        return goal

    async def get_daily_goal(self, squad_id: UUID, user: User) -> Optional[SquadDailyGoal]:
        """
        Get squad daily goal.

        Args:
            squad_id: UUID of the squad
            user: User requesting the goal

        Returns:
            SquadDailyGoal object if found and user has access, None otherwise

        Raises:
            PermissionDeniedError: If user cannot access the squad
        """
        # Check permissions
        can_access = await can_access_squad(self.db, user, squad_id)
        if not can_access:
            raise PermissionDeniedError(
                f"User {user.id} does not have access to squad {squad_id}"
            )

        stmt = (
            select(SquadDailyGoal)
            .options(
                selectinload(SquadDailyGoal.squad),
                selectinload(SquadDailyGoal.created_by),
                selectinload(SquadDailyGoal.completed_by),
            )
            .where(SquadDailyGoal.squad_id == squad_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_daily_goal(
        self,
        user: User,
        squad_id: UUID,
        goal_text: Optional[str] = None,
        is_completed: Optional[bool] = None,
        metadata: Optional[dict] = None,
    ) -> SquadDailyGoal:
        """
        Update squad daily goal.

        Only Squad Leaders can update goals.

        Args:
            user: User updating the goal
            squad_id: UUID of the squad
            goal_text: Optional new goal text
            is_completed: Optional completion status
            metadata: Optional metadata update

        Returns:
            Updated SquadDailyGoal object

        Raises:
            PermissionDeniedError: If user cannot manage the squad
            GoalNotFoundError: If goal doesn't exist
        """
        # Check permissions
        can_manage = await can_manage_squad(self.db, user, squad_id)
        if not can_manage:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to update goal for squad {squad_id}"
            )

        # Get goal
        stmt = select(SquadDailyGoal).where(SquadDailyGoal.squad_id == squad_id)
        result = await self.db.execute(stmt)
        goal = result.scalar_one_or_none()

        if not goal:
            raise GoalNotFoundError(f"Daily goal not found for squad {squad_id}")

        # Update fields
        if goal_text is not None:
            goal.goal_text = goal_text
        if is_completed is not None:
            goal.is_completed = is_completed
            if is_completed and not goal.completed_at:
                goal.completed_at = datetime.now(timezone.utc)
                goal.completed_by_id = user.id
            elif not is_completed:
                goal.completed_at = None
                goal.completed_by_id = None
        if metadata is not None:
            goal.metadata = {**goal.metadata, **metadata}

        goal.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        return goal

    async def get_squad_dashboard(
        self,
        squad_id: UUID,
        user: User,
        upcoming_days: int = 7,
    ) -> dict:
        """
        Get squad schedule dashboard with efficient queries.

        Optimized for dashboard loading with minimal database hits.

        Args:
            squad_id: UUID of the squad
            user: User requesting dashboard
            upcoming_days: Number of days to look ahead for events

        Returns:
            Dictionary with dashboard data

        Raises:
            PermissionDeniedError: If user cannot access the squad
        """
        # Check permissions
        can_access = await can_access_squad(self.db, user, squad_id)
        if not can_access:
            raise PermissionDeniedError(
                f"User {user.id} does not have access to squad {squad_id}"
            )

        # Get squad
        squad_stmt = select(Squad).where(Squad.id == squad_id)
        squad_result = await self.db.execute(squad_stmt)
        squad = squad_result.scalar_one_or_none()

        if not squad:
            raise SquadNotFoundError(f"Squad {squad_id} not found")

        # Get upcoming events (efficient query with date range)
        from datetime import timedelta

        now = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        end_date = end_date + timedelta(days=upcoming_days)

        events, event_count = await self.get_squad_events(
            squad_id=squad_id,
            user=user,
            start_date=now,
            end_date=end_date,
            limit=20,  # Limit for dashboard
        )

        # Get current daily goal
        goal = await self.get_daily_goal(squad_id, user)

        # Calculate goal completion rate (for analytics)
        # This is a placeholder - in production, you'd query historical goals
        goal_completion_rate = None
        if goal:
            # Future: Query historical goals and calculate rate
            # For now, just return None
            pass

        return {
            "squad_id": squad_id,
            "squad_name": squad.name,
            "upcoming_events": events,
            "current_goal": goal,
            "event_count": event_count,
            "goal_completion_rate": goal_completion_rate,
        }
