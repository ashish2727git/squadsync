"""
SquadSync Database Models
Production-grade SQLAlchemy models for the gaming platform hierarchy.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class UserRole(str, Enum):
    """User role enumeration for hierarchical permissions."""

    ORG_ADMIN = "ORG_ADMIN"
    TEAM_MANAGER = "TEAM_MANAGER"
    SQUAD_LEADER = "SQUAD_LEADER"
    PLAYER = "PLAYER"


class SummonStatus(str, Enum):
    """Summon status enumeration."""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ResponseType(str, Enum):
    """Summon response type enumeration."""

    PENDING = "PENDING"
    ACCEPT = "ACCEPT"
    DECLINE = "DECLINE"
    MAYBE = "MAYBE"


# Association table for many-to-many relationship between Squad and User
squad_membership_table = Table(
    "squad_membership",
    Base.metadata,
    Column("squad_id", PostgreSQLUUID(as_uuid=True), ForeignKey("squad.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), primary_key=True),
    Column("joined_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
)


class Organization(Base):
    """Organization model - top level in hierarchy."""

    __tablename__ = "organization"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    teams: Mapped[list["Team"]] = relationship(
        "Team",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    organization_admins: Mapped[list["OrganizationAdmin"]] = relationship(
        "OrganizationAdmin",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name})>"


class Team(Base):
    """Team model - second level in hierarchy, belongs to Organization."""

    __tablename__ = "team"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    organization_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="teams",
    )
    squads: Mapped[list["Squad"]] = relationship(
        "Squad",
        back_populates="team",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    team_managers: Mapped[list["TeamManager"]] = relationship(
        "TeamManager",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name={self.name}, organization_id={self.organization_id})>"


class Squad(Base):
    """Squad model - third level in hierarchy, belongs to Team."""

    __tablename__ = "squad"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_members: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="squads",
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        secondary=squad_membership_table,
        back_populates="squads",
        lazy="selectin",
    )
    squad_leaders: Mapped[list["SquadLeader"]] = relationship(
        "SquadLeader",
        back_populates="squad",
        cascade="all, delete-orphan",
    )
    summons: Mapped[list["Summon"]] = relationship(
        "Summon",
        back_populates="squad",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["SquadEvent"]] = relationship(
        "SquadEvent",
        back_populates="squad",
        cascade="all, delete-orphan",
    )
    daily_goal: Mapped[Optional["SquadDailyGoal"]] = relationship(
        "SquadDailyGoal",
        back_populates="squad",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Squad(id={self.id}, name={self.name}, team_id={self.team_id})>"


class User(Base):
    """User model - base player/user in the system."""

    __tablename__ = "app_user"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False),
        default=UserRole.PLAYER,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    squads: Mapped[list["Squad"]] = relationship(
        "Squad",
        secondary=squad_membership_table,
        back_populates="members",
    )
    organization_admin_roles: Mapped[list["OrganizationAdmin"]] = relationship(
        "OrganizationAdmin",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    team_manager_roles: Mapped[list["TeamManager"]] = relationship(
        "TeamManager",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    squad_leader_roles: Mapped[list["SquadLeader"]] = relationship(
        "SquadLeader",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    player_vault: Mapped[Optional["PlayerVault"]] = relationship(
        "PlayerVault",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    created_summons: Mapped[list["Summon"]] = relationship(
        "Summon",
        foreign_keys="[Summon.created_by_id]",
        back_populates="created_by",
    )
    summon_responses: Mapped[list["SummonResponse"]] = relationship(
        "SummonResponse",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


class OrganizationAdmin(Base):
    """Junction table for Organization admin assignments."""

    __tablename__ = "organization_admin"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    organization_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="organization_admins",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organization_admin_roles",
    )

    def __repr__(self) -> str:
        return f"<OrganizationAdmin(organization_id={self.organization_id}, user_id={self.user_id})>"


class TeamManager(Base):
    """Junction table for Team manager assignments."""

    __tablename__ = "team_manager"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    team_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="team_managers",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="team_manager_roles",
    )

    def __repr__(self) -> str:
        return f"<TeamManager(team_id={self.team_id}, user_id={self.user_id})>"


class SquadLeader(Base):
    """Junction table for Squad leader assignments."""

    __tablename__ = "squad_leader"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    squad_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("squad.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    squad: Mapped["Squad"] = relationship(
        "Squad",
        back_populates="squad_leaders",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="squad_leader_roles",
    )

    def __repr__(self) -> str:
        return f"<SquadLeader(squad_id={self.squad_id}, user_id={self.user_id})>"


class PlayerVault(Base):
    """Private user data storage - one-to-one with User."""

    __tablename__ = "player_vault"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    vault_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="player_vault",
    )

    def __repr__(self) -> str:
        return f"<PlayerVault(id={self.id}, user_id={self.user_id})>"


class Summon(Base):
    """Summon model - invitations or requests within a Squad."""

    __tablename__ = "summon"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    squad_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("squad.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[SummonStatus] = mapped_column(
        SQLEnum(SummonStatus, native_enum=False),
        default=SummonStatus.PENDING,
        nullable=False,
        index=True,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    squad: Mapped["Squad"] = relationship(
        "Squad",
        back_populates="summons",
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_summons",
    )
    responses: Mapped[list["SummonResponse"]] = relationship(
        "SummonResponse",
        back_populates="summon",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Summon(id={self.id}, squad_id={self.squad_id}, status={self.status})>"


class SummonResponse(Base):
    """SummonResponse model - user responses to Summons."""

    __tablename__ = "summon_response"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    summon_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("summon.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    response_type: Mapped[ResponseType] = mapped_column(
        SQLEnum(ResponseType, native_enum=False),
        nullable=False,
        index=True,
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    summon: Mapped["Summon"] = relationship(
        "Summon",
        back_populates="responses",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="summon_responses",
    )

    def __repr__(self) -> str:
        return f"<SummonResponse(id={self.id}, summon_id={self.summon_id}, user_id={self.user_id}, response_type={self.response_type})>"


class SquadEvent(Base):
    """Squad calendar event model - squad-only scheduling."""

    __tablename__ = "squad_event"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    squad_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("squad.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        default="general",
        nullable=False,
        index=True,
    )  # e.g., "practice", "match", "meeting", "general"
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # e.g., "daily", "weekly", "monthly"
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # For future analytics and extensibility
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    squad: Mapped["Squad"] = relationship(
        "Squad",
        back_populates="events",
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )

    def __repr__(self) -> str:
        return f"<SquadEvent(id={self.id}, squad_id={self.squad_id}, title={self.title}, start_time={self.start_time})>"


class SquadDailyGoal(Base):
    """Squad daily goal model - single active goal per squad."""

    __tablename__ = "squad_daily_goal"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    squad_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("squad.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )  # Unique constraint ensures one active goal per squad
    created_by_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    target_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )  # Date this goal is for
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_by_id: Mapped[Optional[UUID]] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("app_user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    metadata: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )  # For future analytics
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    squad: Mapped["Squad"] = relationship(
        "Squad",
        back_populates="daily_goal",
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )
    completed_by: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[completed_by_id],
    )

    def __repr__(self) -> str:
        return f"<SquadDailyGoal(id={self.id}, squad_id={self.squad_id}, target_date={self.target_date})>"
