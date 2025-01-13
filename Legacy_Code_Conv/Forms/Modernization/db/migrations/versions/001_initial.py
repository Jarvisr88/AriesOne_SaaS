"""Initial database schema.

Revision ID: 001_initial
Create Date: 2025-01-11 15:33:02.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_users_username',
        'users',
        ['username'],
        unique=True
    )
    op.create_index(
        'ix_users_email',
        'users',
        ['email'],
        unique=True
    )

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_roles_name',
        'roles',
        ['name'],
        unique=True
    )

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_permissions_name',
        'permissions',
        ['name'],
        unique=True
    )

    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('details', sa.String(length=1024), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_companies_name',
        'companies',
        ['name'],
        unique=False
    )
    op.create_index(
        'ix_companies_code',
        'companies',
        ['code'],
        unique=True
    )

    # Create forms table
    op.create_table(
        'forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('schema', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_forms_name',
        'forms',
        ['name'],
        unique=False
    )

    # Create form_submissions table
    op.create_table(
        'form_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_id', sa.Integer(), nullable=False),
        sa.Column('submitted_by', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
        sa.ForeignKeyConstraint(['submitted_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create company_forms table
    op.create_table(
        'company_forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('form_id', sa.Integer(), nullable=False),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('company_forms')
    op.drop_table('form_submissions')
    op.drop_index('ix_forms_name', table_name='forms')
    op.drop_table('forms')
    op.drop_index('ix_companies_code', table_name='companies')
    op.drop_index('ix_companies_name', table_name='companies')
    op.drop_table('companies')
    op.drop_table('audit_logs')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_index('ix_permissions_name', table_name='permissions')
    op.drop_table('permissions')
    op.drop_index('ix_roles_name', table_name='roles')
    op.drop_table('roles')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
