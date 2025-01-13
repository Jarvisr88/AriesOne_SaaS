"""
Security Models Migration
Version: 1.0.0
Last Updated: 2025-01-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '002_security'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create role table
    op.create_table(
        'role',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_role')),
        sa.UniqueConstraint('name', name=op.f('uq_role_name'))
    )
    
    # Create permission table
    op.create_table(
        'permission',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_permission')),
        sa.UniqueConstraint('name', name=op.f('uq_permission_name'))
    )
    
    # Create role_permissions association table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'],
                              name=op.f('fk_role_permissions_permission_id_permission')),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'],
                              name=op.f('fk_role_permissions_role_id_role')),
        sa.PrimaryKeyConstraint('role_id', 'permission_id',
                              name=op.f('pk_role_permissions'))
    )
    
    # Create user_roles association table
    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'],
                              name=op.f('fk_user_roles_role_id_role')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                              name=op.f('fk_user_roles_user_id_user')),
        sa.PrimaryKeyConstraint('user_id', 'role_id',
                              name=op.f('pk_user_roles'))
    )
    
    # Create security_audit_log table
    op.create_table(
        'securityauditlog',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('details', sa.String(length=500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                              name=op.f('fk_securityauditlog_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_securityauditlog'))
    )
    
    # Create access_token table
    op.create_table(
        'accesstoken',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('scope', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                              name=op.f('fk_accesstoken_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_accesstoken'))
    )
    
    # Create refresh_token table
    op.create_table(
        'refreshtoken',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('access_token_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['access_token_id'], ['accesstoken.id'],
                              name=op.f('fk_refreshtoken_access_token_id_accesstoken')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'],
                              name=op.f('fk_refreshtoken_user_id_user')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_refreshtoken'))
    )
    
    # Create indexes
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)
    op.create_index(op.f('ix_permission_name'), 'permission', ['name'], unique=True)
    op.create_index(op.f('ix_permission_resource'), 'permission', ['resource'], unique=False)
    op.create_index(op.f('ix_permission_action'), 'permission', ['action'], unique=False)
    op.create_index(op.f('ix_securityauditlog_event_type'), 'securityauditlog',
                   ['event_type'], unique=False)
    op.create_index(op.f('ix_securityauditlog_user_id'), 'securityauditlog',
                   ['user_id'], unique=False)
    op.create_index(op.f('ix_accesstoken_user_id'), 'accesstoken',
                   ['user_id'], unique=False)
    op.create_index(op.f('ix_accesstoken_token'), 'accesstoken',
                   ['token'], unique=True)
    op.create_index(op.f('ix_refreshtoken_user_id'), 'refreshtoken',
                   ['user_id'], unique=False)
    op.create_index(op.f('ix_refreshtoken_token'), 'refreshtoken',
                   ['token'], unique=True)
    op.create_index(op.f('ix_refreshtoken_access_token_id'), 'refreshtoken',
                   ['access_token_id'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('refreshtoken')
    op.drop_table('accesstoken')
    op.drop_table('securityauditlog')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('permission')
    op.drop_table('role')
