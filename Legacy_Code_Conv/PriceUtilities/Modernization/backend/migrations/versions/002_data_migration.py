"""Data migration from legacy system

Revision ID: 002_data_migration
Create Date: 2025-01-12 11:19:49.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import json
import csv
from pathlib import Path

# revision identifiers, used by Alembic
revision = '002_data_migration'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

def get_legacy_data(file_path):
    """Read data from legacy CSV file"""
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def upgrade():
    # Get connection
    connection = op.get_bind()
    
    # Create admin user first
    admin_user_query = """
    INSERT INTO users (email, name, role, department)
    VALUES ('admin@company.com', 'System Admin', 'admin', 'IT')
    RETURNING id;
    """
    admin_id = connection.execute(sa.text(admin_user_query)).scalar()

    # Migrate price list data
    price_list_data = get_legacy_data('legacy_data/price_list.csv')
    for item in price_list_data:
        # Convert quantity breaks from string to JSONB
        quantity_breaks = json.loads(item.get('quantity_breaks', '{}'))
        
        query = """
        INSERT INTO price_list (
            item_id, description, base_price, currency,
            quantity_breaks, effective_date, created_by, updated_by
        )
        VALUES (
            :item_id, :description, :base_price, :currency,
            :quantity_breaks, :effective_date, :admin_id, :admin_id
        );
        """
        connection.execute(
            sa.text(query),
            {
                'item_id': item['item_id'],
                'description': item['description'],
                'base_price': float(item['base_price']),
                'currency': item['currency'],
                'quantity_breaks': json.dumps(quantity_breaks),
                'effective_date': datetime.now(),
                'admin_id': admin_id
            }
        )

    # Migrate ICD codes
    icd_codes_data = get_legacy_data('legacy_data/icd_codes.csv')
    for code in icd_codes_data:
        query = """
        INSERT INTO icd_codes (
            code, description, price_modifier,
            effective_date, created_by, updated_by
        )
        VALUES (
            :code, :description, :price_modifier,
            :effective_date, :admin_id, :admin_id
        );
        """
        connection.execute(
            sa.text(query),
            {
                'code': code['code'],
                'description': code['description'],
                'price_modifier': float(code['price_modifier']),
                'effective_date': datetime.now(),
                'admin_id': admin_id
            }
        )

    # Migrate parameters
    parameters_data = get_legacy_data('legacy_data/parameters.csv')
    for param in parameters_data:
        query = """
        INSERT INTO parameters (
            name, value, parameter_type, description,
            effective_date, created_by, updated_by
        )
        VALUES (
            :name, :value, :parameter_type, :description,
            :effective_date, :admin_id, :admin_id
        );
        """
        connection.execute(
            sa.text(query),
            {
                'name': param['name'],
                'value': float(param['value']),
                'parameter_type': param['parameter_type'],
                'description': param['description'],
                'effective_date': datetime.now(),
                'admin_id': admin_id
            }
        )

    # Create audit log entries for initial data migration
    tables = ['price_list', 'icd_codes', 'parameters']
    for table in tables:
        query = f"""
        INSERT INTO audit_log (
            table_name, record_id, action, changes, created_by
        )
        SELECT 
            '{table}' as table_name,
            id as record_id,
            'INSERT' as action,
            jsonb_build_object(
                'operation', 'initial_migration',
                'timestamp', now()
            ) as changes,
            :admin_id as created_by
        FROM {table};
        """
        connection.execute(sa.text(query), {'admin_id': admin_id})

def downgrade():
    connection = op.get_bind()
    
    # Clear all migrated data
    tables = ['audit_log', 'parameters', 'icd_codes', 'price_list', 'users']
    for table in tables:
        connection.execute(sa.text(f"DELETE FROM {table};"))
