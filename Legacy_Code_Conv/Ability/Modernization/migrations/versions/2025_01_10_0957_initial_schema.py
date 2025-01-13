"""Initial schema

Revision ID: initial_schema
Create Date: 2025-01-10 09:57:00.000000
"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create ability tables
    op.create_table(
        'credentials',
        sa.Column('credential_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('sender_id', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('credential_id')
    )

    op.create_table(
        'clerk_credentials',
        sa.Column('credential_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('sender_id', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('clerk_id', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('permissions', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('credential_id')
    )

    op.create_table(
        'eligibility_credentials',
        sa.Column('credential_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('sender_id', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('facility_id', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('credential_id')
    )

    op.create_table(
        'envelope_credentials',
        sa.Column('credential_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('sender_id', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('envelope_id', sa.String(length=100), nullable=False),
        sa.Column('environment', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('credential_id')
    )

    op.create_table(
        'integration_settings',
        sa.Column('settings_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('credentials_id', postgresql.UUID(), nullable=True),
        sa.Column('clerk_credentials_id', postgresql.UUID(), nullable=True),
        sa.Column('eligibility_credentials_id', postgresql.UUID(), nullable=True),
        sa.Column('envelope_credentials_id', postgresql.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['credentials_id'], ['credentials.credential_id'], ),
        sa.ForeignKeyConstraint(['clerk_credentials_id'], ['clerk_credentials.credential_id'], ),
        sa.ForeignKeyConstraint(['eligibility_credentials_id'], ['eligibility_credentials.credential_id'], ),
        sa.ForeignKeyConstraint(['envelope_credentials_id'], ['envelope_credentials.credential_id'], ),
        sa.PrimaryKeyConstraint('settings_id')
    )

    # Create common tables
    op.create_table(
        'errors',
        sa.Column('error_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('user_id', postgresql.UUID(), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('error_id')
    )

    op.create_table(
        'file_metadata',
        sa.Column('file_id', postgresql.UUID(), nullable=False, default=uuid4),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('file_id')
    )

    # Create indexes
    op.create_index(
        'ix_errors_created_at',
        'errors',
        ['created_at'],
        unique=False
    )
    op.create_index(
        'ix_errors_user_id',
        'errors',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_file_metadata_user_id',
        'file_metadata',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_file_metadata_created_at',
        'file_metadata',
        ['created_at'],
        unique=False
    )

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_file_metadata_created_at', table_name='file_metadata')
    op.drop_index('ix_file_metadata_user_id', table_name='file_metadata')
    op.drop_index('ix_errors_user_id', table_name='errors')
    op.drop_index('ix_errors_created_at', table_name='errors')

    # Drop common tables
    op.drop_table('file_metadata')
    op.drop_table('errors')

    # Drop ability tables
    op.drop_table('integration_settings')
    op.drop_table('envelope_credentials')
    op.drop_table('eligibility_credentials')
    op.drop_table('clerk_credentials')
    op.drop_table('credentials')
