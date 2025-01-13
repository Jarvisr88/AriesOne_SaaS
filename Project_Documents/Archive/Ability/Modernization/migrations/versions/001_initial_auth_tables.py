"""Initial authentication tables.

Revision ID: 001
Revises: 
Create Date: 2025-01-09 18:49:29.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create all authentication tables."""
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_mfa_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('mfa_secret', sa.String(length=32), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    # Create indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_permissions_role_id'), 'permissions', ['role_id'])
    op.create_index(op.f('ix_user_roles_user_id'), 'user_roles', ['user_id'])
    op.create_index(op.f('ix_user_roles_role_id'), 'user_roles', ['role_id'])

def downgrade() -> None:
    """Drop all authentication tables."""
    # Drop indexes
    op.drop_index(op.f('ix_user_roles_role_id'), table_name='user_roles')
    op.drop_index(op.f('ix_user_roles_user_id'), table_name='user_roles')
    op.drop_index(op.f('ix_permissions_role_id'), table_name='permissions')
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')

    # Drop tables
    op.drop_table('refresh_tokens')
    op.drop_table('permissions')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')
