"""Add Tenant Features
Version: 1.0.0
Last Updated: 2025-01-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '002_add_tenant_features'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to tenants table
    op.add_column('tenants',
        sa.Column('features', postgresql.JSONB, server_default='{}')
    )
    op.add_column('tenants',
        sa.Column('billing_cycle', sa.String(50), nullable=False, server_default='monthly')
    )
    op.add_column('tenants',
        sa.Column('next_billing_date', sa.Date())
    )
    op.add_column('tenants',
        sa.Column('api_key', sa.String(255), unique=True)
    )
    
    # Create tenant_settings table
    op.create_table(
        'tenant_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('tenant_id', 'key', name='uix_tenant_settings')
    )
    
    # Create tenant_api_keys table
    op.create_table(
        'tenant_api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('scopes', postgresql.ARRAY(sa.String)),
        sa.Column('expires_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('last_used_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index(
        'ix_tenant_settings_tenant_key',
        'tenant_settings',
        ['tenant_id', 'key']
    )
    op.create_index(
        'ix_tenant_api_keys_tenant',
        'tenant_api_keys',
        ['tenant_id']
    )
    op.create_index(
        'ix_tenant_api_keys_key',
        'tenant_api_keys',
        ['key']
    )
    
    # Add default features for existing tenants
    op.execute("""
        UPDATE tenants
        SET features = '{"max_inventory_items": 1000, "max_orders": 1000, "api_access": true}'::jsonb
        WHERE features = '{}'::jsonb
    """)


def downgrade():
    # Drop indexes
    op.drop_index('ix_tenant_api_keys_key')
    op.drop_index('ix_tenant_api_keys_tenant')
    op.drop_index('ix_tenant_settings_tenant_key')
    
    # Drop tables
    op.drop_table('tenant_api_keys')
    op.drop_table('tenant_settings')
    
    # Drop columns from tenants table
    op.drop_column('tenants', 'api_key')
    op.drop_column('tenants', 'next_billing_date')
    op.drop_column('tenants', 'billing_cycle')
    op.drop_column('tenants', 'features')
