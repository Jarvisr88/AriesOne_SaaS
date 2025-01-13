"""Seed default roles and permissions.

Revision ID: 002
Revises: 001
Create Date: 2025-01-09 18:49:29.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

# Default roles with their permissions
DEFAULT_ROLES = {
    'admin': {
        'description': 'Administrator with full system access',
        'permissions': [
            ('*', '*'),  # All resources, all actions
        ]
    },
    'manager': {
        'description': 'Manager with elevated privileges',
        'permissions': [
            ('users', 'read'),
            ('users', 'create'),
            ('users', 'update'),
            ('reports', '*'),
            ('orders', '*'),
            ('inventory', '*')
        ]
    },
    'user': {
        'description': 'Standard user',
        'permissions': [
            ('users', 'read'),
            ('reports', 'read'),
            ('orders', 'read'),
            ('orders', 'create'),
            ('inventory', 'read')
        ]
    }
}

def upgrade() -> None:
    """Add default roles and permissions."""
    # Get current timestamp
    now = datetime.utcnow()

    # Create connection
    connection = op.get_bind()

    # Insert default roles
    for role_name, role_data in DEFAULT_ROLES.items():
        # Insert role
        result = connection.execute(
            sa.text(
                """
                INSERT INTO roles (name, description, created_at, updated_at)
                VALUES (:name, :description, :created_at, :updated_at)
                RETURNING id
                """
            ),
            {
                'name': role_name,
                'description': role_data['description'],
                'created_at': now,
                'updated_at': now
            }
        )
        role_id = result.scalar()

        # Insert permissions for role
        for resource, action in role_data['permissions']:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO permissions (role_id, resource, action, created_at, updated_at)
                    VALUES (:role_id, :resource, :action, :created_at, :updated_at)
                    """
                ),
                {
                    'role_id': role_id,
                    'resource': resource,
                    'action': action,
                    'created_at': now,
                    'updated_at': now
                }
            )

def downgrade() -> None:
    """Remove default roles and their permissions."""
    connection = op.get_bind()

    # Delete roles (permissions will be cascade deleted)
    for role_name in DEFAULT_ROLES.keys():
        connection.execute(
            sa.text("DELETE FROM roles WHERE name = :name"),
            {'name': role_name}
        )
