"""
Summon Service
Business logic for summon creation, management, and response handling.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.permissions import can_manage_squad
from backend.core.redis_client import get_redis
from backend.models.models import (
    ResponseType,
    Squad,
    Summon,
    SummonResponse,
    SummonStatus,
    User,
    squad_membership_table,
)


class SummonServiceError(Exception):
    """Base exception for summon service errors."""

    pass


class PermissionDeniedError(SummonServiceError):
    """Raised when user lacks required permissions."""

    pass


class SquadNotFoundError(SummonServiceError):
    """Raised when squad is not found."""

    pass


class SummonNotFoundError(SummonServiceError):
    """Raised when summon is not found."""

    pass


class InvalidSummonStateError(SummonServiceError):
    """Raised when summon operation is invalid due to current state."""

    pass


class SummonService:
    """Service for managing summons and responses."""

    def __init__(self, db: AsyncSession):
        """
        Initialize summon service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_summon(
        self,
        user: User,
        squad_id: UUID,
        title: str,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Summon:
        """
        Create a new summon for a squad.

        Only Squad Leaders (or higher roles) can create summons.
        Creates SummonResponse records for all active squad members with PENDING status.

        Args:
            user: User creating the summon
            squad_id: UUID of the squad
            title: Summon title
            description: Optional summon description
            expires_at: Optional expiration time

        Returns:
            Created Summon object with relationships loaded

        Raises:
            PermissionDeniedError: If user cannot manage the squad
            SquadNotFoundError: If squad doesn't exist
        """
        # Check permissions - only squad leaders and above can create summons
        can_manage = await can_manage_squad(self.db, user, squad_id)
        if not can_manage:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to create summons for squad {squad_id}"
            )

        # Verify squad exists and get members
        squad_stmt = (
            select(Squad)
            .options(selectinload(Squad.members))
            .where(and_(Squad.id == squad_id, Squad.is_active == True))
        )
        result = await self.db.execute(squad_stmt)
        squad = result.scalar_one_or_none()

        if not squad:
            raise SquadNotFoundError(f"Squad {squad_id} not found or inactive")

        # Get all active squad members (excluding the creator if they're not a member)
        members_stmt = (
            select(User)
            .join(
                squad_membership_table,
                User.id == squad_membership_table.c.user_id,
            )
            .where(
                and_(
                    squad_membership_table.c.squad_id == squad_id,
                    squad_membership_table.c.is_active == True,
                )
            )
        )
        members_result = await self.db.execute(members_stmt)
        members = members_result.scalars().all()

        if not members:
            raise SummonServiceError(f"Squad {squad_id} has no active members")

        # Create summon record
        summon = Summon(
            squad_id=squad_id,
            created_by_id=user.id,
            title=title,
            description=description,
            status=SummonStatus.PENDING,
            expires_at=expires_at,
        )
        self.db.add(summon)
        await self.db.flush()  # Flush to get summon.id

        # Create SummonResponse records for each squad member with default PENDING status
        response_records = []
        for member in members:
            response = SummonResponse(
                summon_id=summon.id,
                user_id=member.id,
                response_type=ResponseType.PENDING,
            )
            response_records.append(response)
            self.db.add(response)

        await self.db.flush()

        # Publish realtime notification to Redis
        redis = await get_redis()
        notification_data = {
            "event_type": "summon_created",
            "summon_id": str(summon.id),
            "squad_id": str(squad_id),
            "created_by_id": str(user.id),
            "created_by_username": user.username,
            "title": title,
            "description": description,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "member_count": len(members),
        }
        channel = f"squad:{squad_id}:summons"
        await redis.publish(channel, notification_data)

        # Also notify individual members
        for member in members:
            member_channel = f"user:{member.id}:notifications"
            await redis.publish(member_channel, notification_data)

        # Reload summon with relationships
        await self.db.refresh(summon)
        return summon

    async def get_summon_by_id(self, summon_id: UUID, user: User) -> Optional[Summon]:
        """
        Get summon by ID with permission check.

        Args:
            summon_id: UUID of the summon
            user: User requesting the summon

        Returns:
            Summon object if found and user has access, None otherwise

        Raises:
            PermissionDeniedError: If user cannot access the summon
        """
        from backend.core.permissions import can_access_squad

        stmt = (
            select(Summon)
            .options(
                selectinload(Summon.squad),
                selectinload(Summon.created_by),
                selectinload(Summon.responses).selectinload(SummonResponse.user),
            )
            .where(Summon.id == summon_id)
        )
        result = await self.db.execute(stmt)
        summon = result.scalar_one_or_none()

        if not summon:
            return None

        # Check if user can access the squad
        can_access = await can_access_squad(self.db, user, summon.squad_id)
        if not can_access:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to view summon {summon_id}"
            )

        return summon

    async def update_summon_response(
        self,
        user: User,
        summon_id: UUID,
        response_type: ResponseType,
        message: Optional[str] = None,
    ) -> SummonResponse:
        """
        Update user's response to a summon.

        Args:
            user: User responding to the summon
            summon_id: UUID of the summon
            response_type: New response type (ACCEPT, DECLINE, MAYBE)
            message: Optional message with the response

        Returns:
            Updated SummonResponse object

        Raises:
            SummonNotFoundError: If summon doesn't exist
            PermissionDeniedError: If user cannot respond to this summon
            InvalidSummonStateError: If summon is not in a valid state for responses
        """
        # Get summon with squad relationship
        stmt = (
            select(Summon)
            .options(selectinload(Summon.squad))
            .where(Summon.id == summon_id)
        )
        result = await self.db.execute(stmt)
        summon = result.scalar_one_or_none()

        if not summon:
            raise SummonNotFoundError(f"Summon {summon_id} not found")

        # Check if summon is still active
        if summon.status != SummonStatus.PENDING:
            raise InvalidSummonStateError(
                f"Summon {summon_id} is {summon.status.value}, cannot update response"
            )

        # Check if summon has expired
        if summon.expires_at and summon.expires_at < datetime.now(timezone.utc):
            raise InvalidSummonStateError(f"Summon {summon_id} has expired")

        # Verify user is a member of the squad
        member_check_stmt = (
            select(squad_membership_table)
            .where(
                and_(
                    squad_membership_table.c.squad_id == summon.squad_id,
                    squad_membership_table.c.user_id == user.id,
                    squad_membership_table.c.is_active == True,
                )
            )
            .limit(1)
        )
        member_result = await self.db.execute(member_check_stmt)
        if member_result.first() is None:
            raise PermissionDeniedError(
                f"User {user.id} is not a member of squad {summon.squad_id}"
            )

        # Get or create response record
        response_stmt = (
            select(SummonResponse)
            .where(
                and_(
                    SummonResponse.summon_id == summon_id,
                    SummonResponse.user_id == user.id,
                )
            )
        )
        response_result = await self.db.execute(response_stmt)
        response = response_result.scalar_one_or_none()

        if not response:
            # Create new response record
            response = SummonResponse(
                summon_id=summon_id,
                user_id=user.id,
                response_type=response_type,
                message=message,
            )
            self.db.add(response)
        else:
            # Update existing response
            response.response_type = response_type
            response.message = message

        await self.db.flush()
        await self.db.refresh(response)

        # Get response counts for notification
        counts_stmt = (
            select(
                SummonResponse.response_type,
                func.count(SummonResponse.id).label("count"),
            )
            .where(SummonResponse.summon_id == summon_id)
            .group_by(SummonResponse.response_type)
        )
        counts_result = await self.db.execute(counts_stmt)
        response_counts = {row[0].value: row[1] for row in counts_result.all()}

        # Publish realtime notification to Redis
        redis = await get_redis()
        notification_data = {
            "event_type": "summon_response_updated",
            "summon_id": str(summon_id),
            "squad_id": str(summon.squad_id),
            "user_id": str(user.id),
            "username": user.username,
            "response_type": response_type.value,
            "message": message,
            "response_counts": response_counts,
        }

        # Notify squad channel
        squad_channel = f"squad:{summon.squad_id}:summons"
        await redis.publish(squad_channel, notification_data)

        # Notify summon creator specifically
        if summon.created_by_id:
            creator_channel = f"user:{summon.created_by_id}:notifications"
            await redis.publish(creator_channel, notification_data)

        return response

    async def get_summon_responses(
        self,
        summon_id: UUID,
        user: User,
    ) -> list[SummonResponse]:
        """
        Get all responses for a summon.

        Args:
            summon_id: UUID of the summon
            user: User requesting responses

        Returns:
            List of SummonResponse objects

        Raises:
            SummonNotFoundError: If summon doesn't exist
            PermissionDeniedError: If user cannot access the summon
        """
        from backend.core.permissions import can_access_squad

        # Verify summon exists and get it
        summon = await self.get_summon_by_id(summon_id, user)
        if not summon:
            raise SummonNotFoundError(f"Summon {summon_id} not found")

        # Get all responses with user information
        stmt = (
            select(SummonResponse)
            .options(selectinload(SummonResponse.user))
            .where(SummonResponse.summon_id == summon_id)
            .order_by(SummonResponse.created_at)
        )
        result = await self.db.execute(stmt)
        responses = result.scalars().all()

        return list(responses)
