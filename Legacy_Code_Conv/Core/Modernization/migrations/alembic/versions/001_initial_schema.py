"""Initial Schema Migration
Version: 1.0.0
Last Updated: 2025-01-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create extension for UUID support
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
    )
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), unique=True, nullable=False),
        sa.Column('subscription_plan', sa.String(50), nullable=False),
        sa.Column('max_users', sa.Integer(), default=5),
        sa.Column('max_storage', sa.BigInteger(), default=5368709120),  # 5GB
        sa.Column('used_storage', sa.BigInteger(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
    )
    
    # Create inventory_items table
    op.create_table(
        'inventory_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(100)),
        sa.Column('status', sa.String(50), default='available'),
        sa.Column('quantity', sa.Integer(), default=0),
        sa.Column('unit_price', sa.Numeric(10, 2)),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('order_number', sa.String(50), unique=True, nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('customer_email', sa.String(255)),
        sa.Column('shipping_address', sa.Text()),
        sa.Column('billing_address', sa.Text()),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('total', sa.Numeric(10, 2), default=0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount', sa.Numeric(10, 2), default=0),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ondelete='RESTRICT'),
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True)),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('details', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_tenants_slug', 'tenants', ['slug'])
    op.create_index('ix_inventory_items_tenant_id', 'inventory_items', ['tenant_id'])
    op.create_index('ix_inventory_items_category', 'inventory_items', ['category'])
    op.create_index('ix_orders_tenant_id', 'orders', ['tenant_id'])
    op.create_index('ix_orders_order_number', 'orders', ['order_number'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_audit_logs_action')
    op.drop_index('ix_audit_logs_user_id')
    op.drop_index('ix_audit_logs_tenant_id')
    op.drop_index('ix_orders_status')
    op.drop_index('ix_orders_order_number')
    op.drop_index('ix_orders_tenant_id')
    op.drop_index('ix_inventory_items_category')
    op.drop_index('ix_inventory_items_tenant_id')
    op.drop_index('ix_tenants_slug')
    op.drop_index('ix_users_tenant_id')
    op.drop_index('ix_users_email')
    
    # Drop tables
    op.drop_table('audit_logs')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('inventory_items')
    op.drop_table('tenants')
    op.drop_table('users')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
