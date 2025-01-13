"""Migrate existing credentials data.

Revision ID: 004
Revises: 003
Create Date: 2025-01-09 18:52:54.000000
"""
from datetime import datetime
import json
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Migrate existing credentials to new schema."""
    # Create temporary table for old credentials
    op.create_table(
        'temp_old_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('token', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Get connection and create session
    connection = op.get_bind()
    session = Session(bind=connection)

    try:
        # Copy data from old table (assuming it exists)
        connection.execute("""
            INSERT INTO temp_old_credentials (id, username, password, api_key, token, created_at)
            SELECT id, username, password, api_key, token, created_at
            FROM ability_credentials
        """)

        # Get current timestamp
        now = datetime.utcnow()

        # Migrate password credentials
        connection.execute("""
            INSERT INTO credentials (
                name,
                description,
                type,
                status,
                encrypted_value,
                metadata,
                created_at,
                updated_at
            )
            SELECT 
                username || '_password' as name,
                'Migrated password credential' as description,
                'password'::credential_type as type,
                'active'::credential_status as status,
                password as encrypted_value,
                jsonb_build_object(
                    'migrated_from', 'ability_credentials',
                    'original_username', username
                ) as metadata,
                COALESCE(created_at, :now) as created_at,
                :now as updated_at
            FROM temp_old_credentials
            WHERE password IS NOT NULL
        """, {"now": now})

        # Migrate API keys
        connection.execute("""
            INSERT INTO credentials (
                name,
                description,
                type,
                status,
                encrypted_value,
                metadata,
                created_at,
                updated_at
            )
            SELECT 
                username || '_api_key' as name,
                'Migrated API key credential' as description,
                'api_key'::credential_type as type,
                'active'::credential_status as status,
                api_key as encrypted_value,
                jsonb_build_object(
                    'migrated_from', 'ability_credentials',
                    'original_username', username
                ) as metadata,
                COALESCE(created_at, :now) as created_at,
                :now as updated_at
            FROM temp_old_credentials
            WHERE api_key IS NOT NULL
        """, {"now": now})

        # Migrate tokens
        connection.execute("""
            INSERT INTO credentials (
                name,
                description,
                type,
                status,
                encrypted_value,
                metadata,
                created_at,
                updated_at
            )
            SELECT 
                username || '_token' as name,
                'Migrated token credential' as description,
                'token'::credential_type as type,
                'active'::credential_status as status,
                token as encrypted_value,
                jsonb_build_object(
                    'migrated_from', 'ability_credentials',
                    'original_username', username
                ) as metadata,
                COALESCE(created_at, :now) as created_at,
                :now as updated_at
            FROM temp_old_credentials
            WHERE token IS NOT NULL
        """, {"now": now})

        # Create audit logs for migrated credentials
        connection.execute("""
            INSERT INTO credential_audit_logs (
                credential_id,
                action,
                details,
                created_at
            )
            SELECT 
                id,
                'migrate',
                jsonb_build_object(
                    'source', 'ability_credentials',
                    'migration_date', :now::text
                ),
                :now
            FROM credentials
            WHERE metadata->>'migrated_from' = 'ability_credentials'
        """, {"now": now})

        # Drop temporary table
        op.drop_table('temp_old_credentials')

    except Exception as e:
        # If anything fails, drop the temporary table
        op.drop_table('temp_old_credentials')
        raise e

def downgrade() -> None:
    """No downgrade available for data migration."""
    pass
