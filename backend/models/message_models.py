"""
SquadSync Message & Communication Models
Discord-like messaging system with DMs, channels, reactions, and threads.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Table, func, Index
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.models import Base


class ChannelType(str, Enum):
    TEXT = "TEXT"
    VOICE = "VOICE"
    ANNOUNCEMENT = "ANNOUNCEMENT"


class MessageType(str, Enum):
    TEXT = "TEXT"
    SYSTEM = "SYSTEM"
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    FILE = "FILE"


class UserPresence(str, Enum):
    ONLINE = "ONLINE"
    IDLE = "IDLE"
    DND = "DND"
    OFFLINE = "OFFLINE"
    INVISIBLE = "INVISIBLE"


class Channel(Base):
    """Channel model - text/voice channels within a squad."""
    __tablename__ = "channel"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    squad_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("squad.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    channel_type: Mapped[ChannelType] = mapped_column(String(20), default=ChannelType.TEXT, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="channel", cascade="all, delete-orphan")


class Message(Base):
    """Message model - persistent chat messages."""
    __tablename__ = "message"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    channel_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("channel.id", ondelete="CASCADE"), nullable=True, index=True)
    sender_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(String(20), default=MessageType.TEXT, nullable=False)
    reply_to_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("message.id", ondelete="SET NULL"), nullable=True)
    
    # For DMs
    dm_conversation_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("dm_conversation.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Attachments as JSON array
    attachments: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default='[]')
    
    # Mentions stored as user IDs
    mentions: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default='[]')
    
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    channel: Mapped[Optional["Channel"]] = relationship("Channel", back_populates="messages")
    reactions: Mapped[list["MessageReaction"]] = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_message_channel_created', 'channel_id', 'created_at'),
        Index('ix_message_dm_created', 'dm_conversation_id', 'created_at'),
    )


class MessageReaction(Base):
    """Message reactions - emoji reactions on messages."""
    __tablename__ = "message_reaction"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    message_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("message.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False, index=True)
    emoji: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    message: Mapped["Message"] = relationship("Message", back_populates="reactions")

    __table_args__ = (
        Index('ix_reaction_unique', 'message_id', 'user_id', 'emoji', unique=True),
    )


class DMConversation(Base):
    """Direct Message conversation between two users."""
    __tablename__ = "dm_conversation"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user1_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False, index=True)
    user2_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False, index=True)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_dm_users', 'user1_id', 'user2_id', unique=True),
    )


class UserStatus(Base):
    """User presence and status tracking."""
    __tablename__ = "user_status"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    presence: Mapped[UserPresence] = mapped_column(String(20), default=UserPresence.OFFLINE, nullable=False)
    status_text: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    current_activity: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class ReadReceipt(Base):
    """Track last read message per user per channel."""
    __tablename__ = "read_receipt"

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False)
    channel_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("channel.id", ondelete="CASCADE"), nullable=True)
    dm_conversation_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("dm_conversation.id", ondelete="CASCADE"), nullable=True)
    last_read_message_id: Mapped[Optional[UUID]] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("message.id", ondelete="SET NULL"), nullable=True)
    last_read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_read_receipt_user_channel', 'user_id', 'channel_id', unique=True),
        Index('ix_read_receipt_user_dm', 'user_id', 'dm_conversation_id', unique=True),
    )
