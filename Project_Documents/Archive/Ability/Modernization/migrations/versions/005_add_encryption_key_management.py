"""Add encryption key management.

Revision ID: 005
Revises: 004
Create Date: 2025-01-09 18:52:54.000000
"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add encryption key management tables."""
    # Create encryption_keys table
    op.create_table(
        'encryption_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key_id', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('rotated_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_id', 'version', name='uq_encryption_keys_key_id_version')
    )

    # Create key_rotation_logs table
    op.create_table(
        'key_rotation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key_id', sa.String(length=100), nullable=False),
        sa.Column('old_version', sa.Integer(), nullable=False),
        sa.Column('new_version', sa.Integer(), nullable=False),
        sa.Column('rotated_by', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['rotated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        'ix_encryption_keys_key_id',
        'encryption_keys',
        ['key_id'],
        unique=False
    )
    op.create_index(
        'ix_encryption_keys_status',
        'encryption_keys',
        ['status'],
        unique=False
    )
    op.create_index(
        'ix_key_rotation_logs_key_id',
        'key_rotation_logs',
        ['key_id'],
        unique=False
    )
    op.create_index(
        'ix_key_rotation_logs_created_at',
        'key_rotation_logs',
        ['created_at'],
        unique=False
    )

    # Add key version reference to credentials
    op.add_column(
        'credentials',
        sa.Column('encryption_key_version', sa.Integer(), nullable=True)
    )
    op.create_index(
        'ix_credentials_encryption_key_version',
        'credentials',
        ['encryption_key_version'],
        unique=False
    )

def downgrade() -> None:
    """Remove encryption key management tables."""
    # Drop indexes
    op.drop_index('ix_credentials_encryption_key_version', table_name='credentials')
    op.drop_index('ix_key_rotation_logs_created_at', table_name='key_rotation_logs')
    op.drop_index('ix_key_rotation_logs_key_id', table_name='key_rotation_logs')
    op.drop_index('ix_encryption_keys_status', table_name='encryption_keys')
    op.drop_index('ix_encryption_keys_key_id', table_name='encryption_keys')

    # Drop column
    op.drop_column('credentials', 'encryption_key_version')

    # Drop tables
    op.drop_table('key_rotation_logs')
    op.drop_table('encryption_keys')
