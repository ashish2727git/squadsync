"""Add database indexes for performance

Revision ID: 002_add_indexes
Revises: 001_initial_schema
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_indexes'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Squad membership lookup index
    op.create_index(
        'idx_squad_membership_lookup',
        'squad_membership',
        ['squad_id', 'user_id', 'is_active'],
        unique=False
    )
    
    # Summon response lookup index
    op.create_index(
        'idx_summon_response_lookup',
        'summon_response',
        ['summon_id', 'user_id'],
        unique=False
    )
    
    # Squad event date range index
    op.create_index(
        'idx_squad_event_date',
        'squad_event',
        ['squad_id', 'start_time'],
        unique=False
    )
    
    # Squad daily goal lookup
    op.create_index(
        'idx_squad_daily_goal_squad',
        'squad_daily_goal',
        ['squad_id', 'target_date'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_squad_membership_lookup', table_name='squad_membership')
    op.drop_index('idx_summon_response_lookup', table_name='summon_response')
    op.drop_index('idx_squad_event_date', table_name='squad_event')
    op.drop_index('idx_squad_daily_goal_squad', table_name='squad_daily_goal')
