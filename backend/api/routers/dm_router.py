"""
Direct Messages Router - Discord-like DM system.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db, get_current_user
from backend.models.models import User
from backend.models.message_models import DMConversation, Message

router = APIRouter(prefix="/api/v1/dm", tags=["Direct Messages"])


class DMConversationResponse(BaseModel):
    id: UUID
    other_user_id: UUID
    other_username: str
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0

    class Config:
        from_attributes = True


class DMMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
    attachments: List[dict] = []


class DMMessageResponse(BaseModel):
    id: UUID
    content: str
    sender_id: UUID
    sender_username: str
    is_edited: bool
    is_deleted: bool
    created_at: datetime
    edited_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/conversations", response_model=List[DMConversationResponse])
async def get_dm_conversations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get all DM conversations for the current user."""
    result = await db.execute(
        select(DMConversation)
        .where(
            or_(
                DMConversation.user1_id == user.id,
                DMConversation.user2_id == user.id,
            )
        )
        .order_by(desc(DMConversation.last_message_at))
    )
    conversations = result.scalars().all()

    response = []
    for conv in conversations:
        other_id = conv.user2_id if conv.user1_id == user.id else conv.user1_id
        other_user = await db.get(User, other_id)

        # Get last message
        last_msg_result = await db.execute(
            select(Message)
            .where(Message.dm_conversation_id == conv.id)
            .where(Message.is_deleted == False)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = last_msg_result.scalar_one_or_none()

        response.append(DMConversationResponse(
            id=conv.id,
            other_user_id=other_id,
            other_username=other_user.username if other_user else "Unknown",
            last_message=last_msg.content[:100] if last_msg else None,
            last_message_at=conv.last_message_at,
            unread_count=0,
        ))

    return response


@router.post("/conversations/{user_id}", response_model=DMConversationResponse)
async def create_or_get_dm(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create or get existing DM conversation with a user."""
    if user_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot DM yourself")

    other_user = await db.get(User, user_id)
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if conversation exists
    result = await db.execute(
        select(DMConversation).where(
            or_(
                and_(DMConversation.user1_id == user.id, DMConversation.user2_id == user_id),
                and_(DMConversation.user1_id == user_id, DMConversation.user2_id == user.id),
            )
        )
    )
    conv = result.scalar_one_or_none()

    if not conv:
        conv = DMConversation(
            user1_id=user.id,
            user2_id=user_id,
        )
        db.add(conv)
        await db.flush()

    return DMConversationResponse(
        id=conv.id,
        other_user_id=user_id,
        other_username=other_user.username,
        last_message=None,
        last_message_at=conv.last_message_at,
        unread_count=0,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[DMMessageResponse])
async def get_dm_messages(
    conversation_id: UUID,
    before: Optional[UUID] = None,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get messages from a DM conversation."""
    conv = await db.get(DMConversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user1_id != user.id and conv.user2_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = (
        select(Message)
        .where(Message.dm_conversation_id == conversation_id)
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

    response = []
    for msg in reversed(messages):
        sender = await db.get(User, msg.sender_id)
        response.append(DMMessageResponse(
            id=msg.id,
            content=msg.content,
            sender_id=msg.sender_id,
            sender_username=sender.username if sender else "Unknown",
            is_edited=msg.is_edited,
            is_deleted=msg.is_deleted,
            created_at=msg.created_at,
            edited_at=msg.edited_at,
        ))

    return response


@router.post("/conversations/{conversation_id}/messages", response_model=DMMessageResponse)
async def send_dm(
    conversation_id: UUID,
    data: DMMessageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a DM message."""
    conv = await db.get(DMConversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user1_id != user.id and conv.user2_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    message = Message(
        dm_conversation_id=conversation_id,
        sender_id=user.id,
        content=data.content,
        attachments=data.attachments,
    )
    db.add(message)

    conv.last_message_at = datetime.utcnow()
    await db.flush()

    return DMMessageResponse(
        id=message.id,
        content=message.content,
        sender_id=message.sender_id,
        sender_username=user.username,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        created_at=message.created_at,
        edited_at=message.edited_at,
    )
