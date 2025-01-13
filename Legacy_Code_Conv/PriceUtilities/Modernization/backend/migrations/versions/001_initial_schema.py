"""Initial database schema

Revision ID: 001_initial_schema
Create Date: 2025-01-12 11:19:49.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from datetime import datetime

# revision identifiers, used by Alembic
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create price_list table
    op.create_table(
        'price_list',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('item_id', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.String(200)),
        sa.Column('base_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('quantity_breaks', JSONB),
        sa.Column('effective_date', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True))
    )

    # Create icd_codes table
    op.create_table(
        'icd_codes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('description', sa.String(200)),
        sa.Column('price_modifier', sa.Numeric(5, 4)),
        sa.Column('effective_date', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True))
    )

    # Create parameters table
    op.create_table(
        'parameters',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('value', sa.Numeric(10, 4), nullable=False),
        sa.Column('parameter_type', sa.String(20), nullable=False),
        sa.Column('description', sa.String(200)),
        sa.Column('effective_date', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True))
    )

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('table_name', sa.String(50), nullable=False),
        sa.Column('record_id', UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(10), nullable=False),
        sa.Column('changes', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False)
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('department', sa.String(50)),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )

    # Create indexes
    op.create_index('idx_price_list_item_id', 'price_list', ['item_id'])
    op.create_index('idx_price_list_effective_date', 'price_list', ['effective_date'])
    op.create_index('idx_icd_codes_code', 'icd_codes', ['code'])
    op.create_index('idx_icd_codes_effective_date', 'icd_codes', ['effective_date'])
    op.create_index('idx_parameters_name', 'parameters', ['name'])
    op.create_index('idx_parameters_effective_date', 'parameters', ['effective_date'])
    op.create_index('idx_audit_log_table_record', 'audit_log', ['table_name', 'record_id'])
    op.create_index('idx_audit_log_created_at', 'audit_log', ['created_at'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])

    # Add foreign key constraints
    op.create_foreign_key('fk_price_list_created_by', 'price_list', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_price_list_updated_by', 'price_list', 'users', ['updated_by'], ['id'])
    op.create_foreign_key('fk_icd_codes_created_by', 'icd_codes', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_icd_codes_updated_by', 'icd_codes', 'users', ['updated_by'], ['id'])
    op.create_foreign_key('fk_parameters_created_by', 'parameters', 'users', ['created_by'], ['id'])
    op.create_foreign_key('fk_parameters_updated_by', 'parameters', 'users', ['updated_by'], ['id'])
    op.create_foreign_key('fk_audit_log_created_by', 'audit_log', 'users', ['created_by'], ['id'])

def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_price_list_created_by', 'price_list')
    op.drop_constraint('fk_price_list_updated_by', 'price_list')
    op.drop_constraint('fk_icd_codes_created_by', 'icd_codes')
    op.drop_constraint('fk_icd_codes_updated_by', 'icd_codes')
    op.drop_constraint('fk_parameters_created_by', 'parameters')
    op.drop_constraint('fk_parameters_updated_by', 'parameters')
    op.drop_constraint('fk_audit_log_created_by', 'audit_log')

    # Drop indexes
    op.drop_index('idx_price_list_item_id')
    op.drop_index('idx_price_list_effective_date')
    op.drop_index('idx_icd_codes_code')
    op.drop_index('idx_icd_codes_effective_date')
    op.drop_index('idx_parameters_name')
    op.drop_index('idx_parameters_effective_date')
    op.drop_index('idx_audit_log_table_record')
    op.drop_index('idx_audit_log_created_at')
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_role')

    # Drop tables
    op.drop_table('audit_log')
    op.drop_table('parameters')
    op.drop_table('icd_codes')
    op.drop_table('price_list')
    op.drop_table('users')
