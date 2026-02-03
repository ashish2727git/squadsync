"""
Add Message & Communication models for Discord-like features.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision = '002_add_message_models'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Channel table
    op.create_table(
        'channel',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('squad_id', UUID(as_uuid=True), sa.ForeignKey('squad.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('channel_type', sa.String(20), default='TEXT', nullable=False),
        sa.Column('position', sa.Integer, default=0, nullable=False),
        sa.Column('is_default', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # DM Conversation table
    op.create_table(
        'dm_conversation',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user1_id', UUID(as_uuid=True), sa.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user2_id', UUID(as_uuid=True), sa.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_dm_users', 'dm_conversation', ['user1_id', 'user2_id'], unique=True)

    # Message table
    op.create_table(
        'message',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('channel_id', UUID(as_uuid=True), sa.ForeignKey('channel.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('sender_id', UUID(as_uuid=True), sa.ForeignKey('app_user.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('message_type', sa.String(20), default='TEXT', nullable=False),
        sa.Column('reply_to_id', UUID(as_uuid=True), sa.ForeignKey('message.id', ondelete='SET NULL'), nullable=True),
        sa.Column('dm_conversation_id', UUID(as_uuid=True), sa.ForeignKey('dm_conversation.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('attachments', JSONB, nullable=False, server_default='[]'),
        sa.Column('mentions', JSONB, nullable=False, server_default='[]'),
        sa.Column('is_pinned', sa.Boolean, default=False, nullable=False),
        sa.Column('is_edited', sa.Boolean, default=False, nullable=False),
        sa.Column('edited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
    )
    op.create_index('ix_message_channel_created', 'message', ['channel_id', 'created_at'])
    op.create_index('ix_message_dm_created', 'message', ['dm_conversation_id', 'created_at'])

    # Message Reaction table
    op.create_table(
        'message_reaction',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', UUID(as_uuid=True), sa.ForeignKey('message.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('emoji', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_reaction_unique', 'message_reaction', ['message_id', 'user_id', 'emoji'], unique=True)

    # User Status table
    op.create_table(
        'user_status',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('app_user.id', ondelete='CASCADE'), unique=True, nullable=False, index=True),
        sa.Column('presence', sa.String(20), default='OFFLINE', nullable=False),
        sa.Column('status_text', sa.String(128), nullable=True),
        sa.Column('current_activity', sa.String(128), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Read Receipt table
    op.create_table(
        'read_receipt',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('app_user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('channel_id', UUID(as_uuid=True), sa.ForeignKey('channel.id', ondelete='CASCADE'), nullable=True),
        sa.Column('dm_conversation_id', UUID(as_uuid=True), sa.ForeignKey('dm_conversation.id', ondelete='CASCADE'), nullable=True),
        sa.Column('last_read_message_id', UUID(as_uuid=True), sa.ForeignKey('message.id', ondelete='SET NULL'), nullable=True),
        sa.Column('last_read_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_read_receipt_user_channel', 'read_receipt', ['user_id', 'channel_id'], unique=True)
    op.create_index('ix_read_receipt_user_dm', 'read_receipt', ['user_id', 'dm_conversation_id'], unique=True)


def downgrade() -> None:
    op.drop_table('read_receipt')
    op.drop_table('user_status')
    op.drop_table('message_reaction')
    op.drop_table('message')
    op.drop_table('dm_conversation')
    op.drop_table('channel')
