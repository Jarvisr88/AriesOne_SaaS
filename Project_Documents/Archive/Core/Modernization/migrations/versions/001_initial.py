"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-07 12:45:11.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create base tables
    op.create_table(
        'core_audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('entity_name', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('changes', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_core_audit_log_entity_name', 'core_audit_log', ['entity_name'])
    op.create_index('ix_core_audit_log_entity_id', 'core_audit_log', ['entity_id'])

    op.create_table(
        'core_error_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('error_type', sa.String(100), nullable=False),
        sa.Column('error_message', sa.String(), nullable=False),
        sa.Column('stack_trace', sa.String(), nullable=True),
        sa.Column('context', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_core_error_log_error_type', 'core_error_log', ['error_type'])

    # Create auth tables
    op.create_table(
        'core_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    op.create_table(
        'core_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('is_system_role', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'core_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'core_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('token_type', sa.String(50), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('device_info', sa.String(200), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['core_users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create many-to-many relationship tables
    op.create_table(
        'core_user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['core_users.id']),
        sa.ForeignKeyConstraint(['role_id'], ['core_roles.id']),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    op.create_table(
        'core_role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['core_roles.id']),
        sa.ForeignKeyConstraint(['permission_id'], ['core_permissions.id']),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('core_role_permissions')
    op.drop_table('core_user_roles')
    op.drop_table('core_tokens')
    op.drop_table('core_permissions')
    op.drop_table('core_roles')
    op.drop_table('core_users')
    op.drop_index('ix_core_error_log_error_type', 'core_error_log')
    op.drop_table('core_error_log')
    op.drop_index('ix_core_audit_log_entity_id', 'core_audit_log')
    op.drop_index('ix_core_audit_log_entity_name', 'core_audit_log')
    op.drop_table('core_audit_log')
