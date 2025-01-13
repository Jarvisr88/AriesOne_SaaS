"""Add Inventory Tracking
Version: 1.0.0
Last Updated: 2025-01-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '003_add_inventory_tracking'
down_revision = '002_add_tenant_features'
branch_labels = None
depends_on = None


def upgrade():
    # Create inventory_transactions table
    op.create_table(
        'inventory_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inventory_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_item_id', postgresql.UUID(as_uuid=True)),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('previous_quantity', sa.Integer(), nullable=False),
        sa.Column('new_quantity', sa.Integer(), nullable=False),
        sa.Column('reference_number', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create inventory_locations table
    op.create_table(
        'inventory_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('address', sa.Text()),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )
    
    # Create inventory_item_locations table
    op.create_table(
        'inventory_item_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inventory_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), default=0),
        sa.Column('minimum_quantity', sa.Integer(), default=0),
        sa.Column('maximum_quantity', sa.Integer()),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('inventory_item_id', 'location_id', name='uix_item_location')
    )
    
    # Add new columns to inventory_items table
    op.add_column('inventory_items',
        sa.Column('sku', sa.String(100), unique=True)
    )
    op.add_column('inventory_items',
        sa.Column('barcode', sa.String(100), unique=True)
    )
    op.add_column('inventory_items',
        sa.Column('minimum_quantity', sa.Integer(), default=0)
    )
    op.add_column('inventory_items',
        sa.Column('maximum_quantity', sa.Integer())
    )
    op.add_column('inventory_items',
        sa.Column('reorder_point', sa.Integer())
    )
    op.add_column('inventory_items',
        sa.Column('reorder_quantity', sa.Integer())
    )
    
    # Create indexes
    op.create_index(
        'ix_inventory_transactions_item_id',
        'inventory_transactions',
        ['inventory_item_id']
    )
    op.create_index(
        'ix_inventory_transactions_tenant_id',
        'inventory_transactions',
        ['tenant_id']
    )
    op.create_index(
        'ix_inventory_transactions_type',
        'inventory_transactions',
        ['transaction_type']
    )
    op.create_index(
        'ix_inventory_locations_tenant_id',
        'inventory_locations',
        ['tenant_id']
    )
    op.create_index(
        'ix_inventory_item_locations_item_id',
        'inventory_item_locations',
        ['inventory_item_id']
    )
    op.create_index(
        'ix_inventory_item_locations_location_id',
        'inventory_item_locations',
        ['location_id']
    )
    op.create_index(
        'ix_inventory_items_sku',
        'inventory_items',
        ['sku']
    )
    op.create_index(
        'ix_inventory_items_barcode',
        'inventory_items',
        ['barcode']
    )


def downgrade():
    # Drop indexes
    op.drop_index('ix_inventory_items_barcode')
    op.drop_index('ix_inventory_items_sku')
    op.drop_index('ix_inventory_item_locations_location_id')
    op.drop_index('ix_inventory_item_locations_item_id')
    op.drop_index('ix_inventory_locations_tenant_id')
    op.drop_index('ix_inventory_transactions_type')
    op.drop_index('ix_inventory_transactions_tenant_id')
    op.drop_index('ix_inventory_transactions_item_id')
    
    # Drop columns from inventory_items table
    op.drop_column('inventory_items', 'reorder_quantity')
    op.drop_column('inventory_items', 'reorder_point')
    op.drop_column('inventory_items', 'maximum_quantity')
    op.drop_column('inventory_items', 'minimum_quantity')
    op.drop_column('inventory_items', 'barcode')
    op.drop_column('inventory_items', 'sku')
    
    # Drop tables
    op.drop_table('inventory_item_locations')
    op.drop_table('inventory_locations')
    op.drop_table('inventory_transactions')
