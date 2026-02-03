"""
Message Router - Discord-like messaging API endpoints.
Handles messages, reactions, channels, and message history.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.dependencies import get_db, get_current_user
from backend.models.models import User, Squad
from backend.models.message_models import (
    Message, MessageReaction, Channel, ChannelType, MessageType,
    DMConversation, UserStatus, UserPresence, ReadReceipt
)

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


# Schemas
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    channel_id: Optional[UUID] = None
    dm_conversation_id: Optional[UUID] = None
    reply_to_id: Optional[UUID] = None
    attachments: List[dict] = []
    mentions: List[UUID] = []


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    id: UUID
    content: str
    sender_id: Optional[UUID]
    sender_username: Optional[str] = None
    channel_id: Optional[UUID]
    dm_conversation_id: Optional[UUID]
    message_type: str
    reply_to_id: Optional[UUID]
    attachments: List[dict]
    mentions: List[UUID]
    is_pinned: bool
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    edited_at: Optional[datetime]
    reactions: List[dict] = []

    class Config:
        from_attributes = True


class ReactionCreate(BaseModel):
    emoji: str = Field(..., min_length=1, max_length=50)


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    channel_type: ChannelType = ChannelType.TEXT


class ChannelResponse(BaseModel):
    id: UUID
    squad_id: UUID
    name: str
    description: Optional[str]
    channel_type: str
    position: int
    is_default: bool
    created_at: datetime
    unread_count: int = 0

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    presence: UserPresence
    status_text: Optional[str] = Field(None, max_length=128)
    current_activity: Optional[str] = Field(None, max_length=128)


class UserStatusResponse(BaseModel):
    user_id: UUID
    presence: str
    status_text: Optional[str]
    current_activity: Optional[str]
    last_seen_at: datetime

    class Config:
        from_attributes = True


# Channel Endpoints
@router.post("/channels/{squad_id}", response_model=ChannelResponse)
async def create_channel(
    squad_id: UUID,
    data: ChannelCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new channel in a squad."""
    squad = await db.get(Squad, squad_id)
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found")

    max_pos = await db.scalar(
        select(func.coalesce(func.max(Channel.position), 0))
        .where(Channel.squad_id == squad_id)
    )

    channel = Channel(
        squad_id=squad_id,
        name=data.name,
        description=data.description,
        channel_type=data.channel_type,
        position=max_pos + 1,
    )
    db.add(channel)
    await db.flush()
    return channel


@router.get("/channels/{squad_id}", response_model=List[ChannelResponse])
async def get_squad_channels(
    squad_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all channels in a squad."""
    result = await db.execute(
        select(Channel)
        .where(Channel.squad_id == squad_id)
        .order_by(Channel.position)
    )
    return result.scalars().all()


@router.delete("/channels/{channel_id}")
async def delete_channel(
    channel_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a channel."""
    channel = await db.get(Channel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    if channel.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default channel")
    
    await db.delete(channel)
    return {"status": "deleted"}


# Message Endpoints
@router.post("", response_model=MessageResponse)
async def create_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new message."""
    if not data.channel_id and not data.dm_conversation_id:
        raise HTTPException(status_code=400, detail="Must specify channel_id or dm_conversation_id")

    message = Message(
        channel_id=data.channel_id,
        dm_conversation_id=data.dm_conversation_id,
        sender_id=user.id,
        content=data.content,
        reply_to_id=data.reply_to_id,
        attachments=data.attachments,
        mentions=[str(m) for m in data.mentions],
    )
    db.add(message)
    await db.flush()

    # Update DM last_message_at
    if data.dm_conversation_id:
        dm = await db.get(DMConversation, data.dm_conversation_id)
        if dm:
            dm.last_message_at = datetime.utcnow()

    return MessageResponse(
        id=message.id,
        content=message.content,
        sender_id=message.sender_id,
        sender_username=user.username,
        channel_id=message.channel_id,
        dm_conversation_id=message.dm_conversation_id,
        message_type=message.message_type,
        reply_to_id=message.reply_to_id,
        attachments=message.attachments,
        mentions=message.mentions,
        is_pinned=message.is_pinned,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        created_at=message.created_at,
        edited_at=message.edited_at,
        reactions=[],
    )


@router.get("/channel/{channel_id}", response_model=List[MessageResponse])
async def get_channel_messages(
    channel_id: UUID,
    before: Optional[UUID] = None,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get messages from a channel with pagination."""
    query = (
        select(Message)
        .where(Message.channel_id == channel_id)
        .where(Message.is_deleted == False)
        .order_by(desc(Message.created_at))
        .limit(limit)
    )

    if before:
        before_msg = await db.get(Message, before)
        if before_msg:
            query = query.where(Message.created_at < before_msg.created_at)

    result = await db.execute(query)
    messages = result.scalars().all()

    # Get sender usernames
    response = []
    for msg in reversed(messages):
        sender = await db.get(User, msg.sender_id) if msg.sender_id else None
        response.append(MessageResponse(
            id=msg.id,
            content=msg.content,
            sender_id=msg.sender_id,
            sender_username=sender.username if sender else None,
            channel_id=msg.channel_id,
            dm_conversation_id=msg.dm_conversation_id,
            message_type=msg.message_type,
            reply_to_id=msg.reply_to_id,
            attachments=msg.attachments or [],
            mentions=msg.mentions or [],
            is_pinned=msg.is_pinned,
            is_edited=msg.is_edited,
            is_deleted=msg.is_deleted,
            created_at=msg.created_at,
            edited_at=msg.edited_at,
            reactions=[],
        ))
    return response


@router.put("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: UUID,
    data: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Edit a message (only by sender)."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender_id != user.id:
        raise HTTPException(status_code=403, detail="Can only edit your own messages")

    message.content = data.content
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    await db.flush()

    return MessageResponse(
        id=message.id,
        content=message.content,
        sender_id=message.sender_id,
        sender_username=user.username,
        channel_id=message.channel_id,
        dm_conversation_id=message.dm_conversation_id,
        message_type=message.message_type,
        reply_to_id=message.reply_to_id,
        attachments=message.attachments or [],
        mentions=message.mentions or [],
        is_pinned=message.is_pinned,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        created_at=message.created_at,
        edited_at=message.edited_at,
        reactions=[],
    )


@router.delete("/{message_id}")
async def delete_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a message (soft delete)."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender_id != user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own messages")

    message.is_deleted = True
    message.content = "[Message deleted]"
    return {"status": "deleted"}


@router.post("/{message_id}/pin")
async def pin_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Pin/unpin a message."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.is_pinned = not message.is_pinned
    return {"is_pinned": message.is_pinned}


# Reaction Endpoints
@router.post("/{message_id}/reactions", status_code=201)
async def add_reaction(
    message_id: UUID,
    data: ReactionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Add a reaction to a message."""
    message = await db.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Check if reaction already exists
    existing = await db.execute(
        select(MessageReaction).where(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == user.id,
            MessageReaction.emoji == data.emoji,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Reaction already exists")

    reaction = MessageReaction(
        message_id=message_id,
        user_id=user.id,
        emoji=data.emoji,
    )
    db.add(reaction)
    return {"status": "added", "emoji": data.emoji}


@router.delete("/{message_id}/reactions/{emoji}")
async def remove_reaction(
    message_id: UUID,
    emoji: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Remove a reaction from a message."""
    result = await db.execute(
        select(MessageReaction).where(
            MessageReaction.message_id == message_id,
            MessageReaction.user_id == user.id,
            MessageReaction.emoji == emoji,
        )
    )
    reaction = result.scalar_one_or_none()
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")

    await db.delete(reaction)
    return {"status": "removed"}


@router.get("/{message_id}/reactions")
async def get_reactions(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all reactions for a message."""
    result = await db.execute(
        select(MessageReaction).where(MessageReaction.message_id == message_id)
    )
    reactions = result.scalars().all()

    # Group by emoji
    emoji_counts = {}
    for r in reactions:
        if r.emoji not in emoji_counts:
            emoji_counts[r.emoji] = {"emoji": r.emoji, "count": 0, "users": []}
        emoji_counts[r.emoji]["count"] += 1
        emoji_counts[r.emoji]["users"].append(str(r.user_id))

    return list(emoji_counts.values())


# User Status Endpoints
@router.put("/status", response_model=UserStatusResponse)
async def update_status(
    data: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update user presence status."""
    result = await db.execute(
        select(UserStatus).where(UserStatus.user_id == user.id)
    )
    status = result.scalar_one_or_none()

    if not status:
        status = UserStatus(
            user_id=user.id,
            presence=data.presence,
            status_text=data.status_text,
            current_activity=data.current_activity,
        )
        db.add(status)
    else:
        status.presence = data.presence
        status.status_text = data.status_text
        status.current_activity = data.current_activity
        status.last_seen_at = datetime.utcnow()

    await db.flush()
    return status


@router.get("/status/{user_id}", response_model=UserStatusResponse)
async def get_user_status(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a user's status."""
    result = await db.execute(
        select(UserStatus).where(UserStatus.user_id == user_id)
    )
    status = result.scalar_one_or_none()
    if not status:
        return UserStatusResponse(
            user_id=user_id,
            presence="OFFLINE",
            status_text=None,
            current_activity=None,
            last_seen_at=datetime.utcnow(),
        )
    return status


# Search Endpoint
@router.get("/search")
async def search_messages(
    q: str = Query(..., min_length=1),
    channel_id: Optional[UUID] = None,
    squad_id: Optional[UUID] = None,
    limit: int = Query(25, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Search messages."""
    query = (
        select(Message)
        .where(Message.content.ilike(f"%{q}%"))
        .where(Message.is_deleted == False)
        .order_by(desc(Message.created_at))
        .limit(limit)
    )

    if channel_id:
        query = query.where(Message.channel_id == channel_id)

    result = await db.execute(query)
    messages = result.scalars().all()

    response = []
    for msg in messages:
        sender = await db.get(User, msg.sender_id) if msg.sender_id else None
        response.append({
            "id": str(msg.id),
            "content": msg.content,
            "sender_username": sender.username if sender else None,
            "channel_id": str(msg.channel_id) if msg.channel_id else None,
            "created_at": msg.created_at.isoformat(),
        })
    return response
