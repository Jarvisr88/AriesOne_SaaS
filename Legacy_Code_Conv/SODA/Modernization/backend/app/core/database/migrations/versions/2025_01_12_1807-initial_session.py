"""Initial session table

Revision ID: initial_session
Revises: 
Create Date: 2025-01-12 18:07
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'initial_session'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sessions table."""
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        # Constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('token'),
        
        # Indexes
        sa.Index('ix_sessions_token', 'token'),
        sa.Index('ix_sessions_user_id', 'user_id'),
        sa.Index('ix_sessions_expires_at', 'expires_at'),
        sa.Index('ix_sessions_is_active', 'is_active')
    )


def downgrade() -> None:
    """Drop sessions table."""
    op.drop_table('sessions')
