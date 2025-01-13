"""Seed base data

Revision ID: 002_seed_base_data
Revises: 001_initial_schema
Create Date: 2025-01-13
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '002_seed_base_data'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Seed default roles
    op.bulk_insert(
        'roles',
        [
            {
                'name': 'ADMIN',
                'description': 'System Administrator',
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'MANAGER',
                'description': 'Company Manager',
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'USER',
                'description': 'Standard User',
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'BILLING',
                'description': 'Billing Access',
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'name': 'INVENTORY',
                'description': 'Inventory Management',
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Create system company
    op.bulk_insert(
        'companies',
        [
            {
                'name': 'System',
                'code': 'SYS001',
                'is_active': True,
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Get system company ID
    connection = op.get_bind()
    sys_company = connection.execute(
        "SELECT id FROM companies WHERE code = 'SYS001'"
    ).fetchone()

    # Create system admin user
    op.bulk_insert(
        'users',
        [
            {
                'username': 'admin',
                'email': 'admin@system.local',
                'password_hash': 'CHANGE_ON_FIRST_LOGIN',  # This should be changed immediately
                'is_active': True,
                'company_id': sys_company[0],
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Get admin user and role IDs
    admin_user = connection.execute(
        "SELECT id FROM users WHERE username = 'admin'"
    ).fetchone()
    admin_role = connection.execute(
        "SELECT id FROM roles WHERE name = 'ADMIN'"
    ).fetchone()

    # Assign admin role to system admin
    op.bulk_insert(
        'user_roles',
        [
            {
                'user_id': admin_user[0],
                'role_id': admin_role[0],
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Create system location
    op.bulk_insert(
        'locations',
        [
            {
                'company_id': sys_company[0],
                'name': 'System Location',
                'address_line1': 'System',
                'city': 'System',
                'state': 'TX',
                'zip_code': '00000',
                'is_active': True,
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

def downgrade() -> None:
    connection = op.get_bind()
    
    # Delete in reverse order to maintain referential integrity
    connection.execute("DELETE FROM user_roles WHERE created_by = 'system'")
    connection.execute("DELETE FROM users WHERE username = 'admin'")
    connection.execute("DELETE FROM locations WHERE created_by = 'system'")
    connection.execute("DELETE FROM companies WHERE code = 'SYS001'")
    connection.execute("DELETE FROM roles WHERE created_by = 'system'")
