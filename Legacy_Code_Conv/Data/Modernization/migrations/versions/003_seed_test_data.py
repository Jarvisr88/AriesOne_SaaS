"""Seed test data

Revision ID: 003_seed_test_data
Revises: 002_seed_base_data
Create Date: 2025-01-13
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

# revision identifiers
revision = '003_seed_test_data'
down_revision = '002_seed_base_data'
branch_labels = None
depends_on = None

def upgrade() -> None:
    connection = op.get_bind()
    
    # Create test company
    op.bulk_insert(
        'companies',
        [
            {
                'name': 'Test Medical Supply Co',
                'code': 'TEST001',
                'is_active': True,
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Get test company ID
    test_company = connection.execute(
        "SELECT id FROM companies WHERE code = 'TEST001'"
    ).fetchone()

    # Create test locations
    op.bulk_insert(
        'locations',
        [
            {
                'company_id': test_company[0],
                'name': 'Main Office',
                'address_line1': '123 Medical Drive',
                'city': 'Austin',
                'state': 'TX',
                'zip_code': '78701',
                'is_active': True,
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'company_id': test_company[0],
                'name': 'Warehouse',
                'address_line1': '456 Supply Road',
                'city': 'Austin',
                'state': 'TX',
                'zip_code': '78702',
                'is_active': True,
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Create test users
    test_users = [
        {
            'username': 'manager',
            'email': 'manager@test.local',
            'password_hash': 'CHANGE_ON_FIRST_LOGIN',
            'is_active': True,
            'company_id': test_company[0],
            'created_by': 'system',
            'updated_by': 'system',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'username': 'billing',
            'email': 'billing@test.local',
            'password_hash': 'CHANGE_ON_FIRST_LOGIN',
            'is_active': True,
            'company_id': test_company[0],
            'created_by': 'system',
            'updated_by': 'system',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'username': 'inventory',
            'email': 'inventory@test.local',
            'password_hash': 'CHANGE_ON_FIRST_LOGIN',
            'is_active': True,
            'company_id': test_company[0],
            'created_by': 'system',
            'updated_by': 'system',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    op.bulk_insert('users', test_users)

    # Assign roles to test users
    manager = connection.execute(
        "SELECT id FROM users WHERE username = 'manager'"
    ).fetchone()
    billing = connection.execute(
        "SELECT id FROM users WHERE username = 'billing'"
    ).fetchone()
    inventory = connection.execute(
        "SELECT id FROM users WHERE username = 'inventory'"
    ).fetchone()

    manager_role = connection.execute(
        "SELECT id FROM roles WHERE name = 'MANAGER'"
    ).fetchone()
    billing_role = connection.execute(
        "SELECT id FROM roles WHERE name = 'BILLING'"
    ).fetchone()
    inventory_role = connection.execute(
        "SELECT id FROM roles WHERE name = 'INVENTORY'"
    ).fetchone()

    op.bulk_insert(
        'user_roles',
        [
            {
                'user_id': manager[0],
                'role_id': manager_role[0],
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'user_id': billing[0],
                'role_id': billing_role[0],
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'user_id': inventory[0],
                'role_id': inventory_role[0],
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Create test price list
    op.bulk_insert(
        'price_lists',
        [
            {
                'company_id': test_company[0],
                'name': 'Standard Price List 2025',
                'code': 'STD2025',
                'is_active': True,
                'effective_date': datetime.utcnow(),
                'expiration_date': datetime.utcnow() + timedelta(days=365),
                'created_by': 'system',
                'updated_by': 'system',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
    )

    # Get price list ID
    price_list = connection.execute(
        "SELECT id FROM price_lists WHERE code = 'STD2025'"
    ).fetchone()

    # Create test price list items
    test_items = []
    for i in range(1, 11):
        test_items.append({
            'price_list_id': price_list[0],
            'item_code': f'ITEM{i:03d}',
            'description': f'Test Item {i}',
            'unit_price': i * 1000,  # Price in cents
            'is_active': True,
            'created_by': 'system',
            'updated_by': 'system',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
    op.bulk_insert('price_list_items', test_items)

def downgrade() -> None:
    connection = op.get_bind()
    
    # Delete test data in reverse order
    connection.execute("DELETE FROM price_list_items WHERE created_by = 'system'")
    connection.execute("DELETE FROM price_lists WHERE code = 'STD2025'")
    connection.execute("DELETE FROM user_roles WHERE created_by = 'system' AND user_id IN (SELECT id FROM users WHERE company_id = (SELECT id FROM companies WHERE code = 'TEST001'))")
    connection.execute("DELETE FROM users WHERE company_id = (SELECT id FROM companies WHERE code = 'TEST001')")
    connection.execute("DELETE FROM locations WHERE company_id = (SELECT id FROM companies WHERE code = 'TEST001')")
    connection.execute("DELETE FROM companies WHERE code = 'TEST001'")
