"""
Create Credentials Table Migration
This module creates the initial credentials table.
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '1234567890ab'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create credentials table"""
    op.create_table(
        'credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.String(length=50), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.LargeBinary(), nullable=False),
        sa.Column('password_salt', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sender_id'),
        sa.UniqueConstraint('username')
    )
    op.create_index(
        op.f('ix_credentials_sender_id'),
        'credentials',
        ['sender_id'],
        unique=True
    )
    op.create_index(
        op.f('ix_credentials_username'),
        'credentials',
        ['username'],
        unique=True
    )

def downgrade():
    """Drop credentials table"""
    op.drop_index(op.f('ix_credentials_username'), table_name='credentials')
    op.drop_index(op.f('ix_credentials_sender_id'), table_name='credentials')
    op.drop_table('credentials')
