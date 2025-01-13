"""Domain entities migration

Revision ID: domain_entities
Revises: initial_session
Create Date: 2025-01-12 18:09
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'domain_entities'
down_revision: str = 'initial_session'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create domain entity tables."""
    # Create enum types
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'manager', 'staff', 'user')")
    op.execute("CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending')")
    op.execute("CREATE TYPE organization_type AS ENUM ('provider', 'supplier', 'partner', 'client')")
    op.execute("CREATE TYPE organization_status AS ENUM ('active', 'inactive', 'suspended', 'pending')")
    op.execute("CREATE TYPE dmerc_form_type AS ENUM ('cmn', 'dif', 'authorization', 'prescription', 'order')")
    op.execute("CREATE TYPE dmerc_status AS ENUM ('draft', 'pending', 'submitted', 'approved', 'denied', 'expired', 'cancelled')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(50)),
        sa.Column('last_name', sa.String(50)),
        sa.Column('phone', sa.String(20)),
        sa.Column('role', postgresql.ENUM('admin', 'manager', 'staff', 'user', name='user_role'), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'suspended', 'pending', name='user_status'), nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('is_2fa_enabled', sa.Boolean(), default=False),
        sa.Column('preferences', postgresql.JSONB),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('email_verified_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('type', postgresql.ENUM('provider', 'supplier', 'partner', 'client', name='organization_type'), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'suspended', 'pending', name='organization_status'), nullable=False),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(20)),
        sa.Column('fax', sa.String(20)),
        sa.Column('website', sa.String(255)),
        sa.Column('address_line1', sa.String(255)),
        sa.Column('address_line2', sa.String(255)),
        sa.Column('city', sa.String(100)),
        sa.Column('state', sa.String(50)),
        sa.Column('postal_code', sa.String(20)),
        sa.Column('country', sa.String(50)),
        sa.Column('tax_id', sa.String(50)),
        sa.Column('npi', sa.String(20)),
        sa.Column('medicare_id', sa.String(20)),
        sa.Column('medicaid_id', sa.String(20)),
        sa.Column('settings', postgresql.JSONB),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.UniqueConstraint('code'),
        sa.ForeignKeyConstraint(['parent_id'], ['organizations.id'], ondelete='SET NULL')
    )
    
    # Create user_organizations table
    op.create_table(
        'user_organizations',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permissions', postgresql.JSONB),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE')
    )
    
    # Create dmerc_forms table
    op.create_table(
        'dmerc_forms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('form_type', postgresql.ENUM('cmn', 'dif', 'authorization', 'prescription', 'order', name='dmerc_form_type'), nullable=False),
        sa.Column('form_number', sa.String(50), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'submitted', 'approved', 'denied', 'expired', 'cancelled', name='dmerc_status'), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by_id', postgresql.UUID(as_uuid=True)),
        sa.Column('patient_id', sa.String(50), nullable=False),
        sa.Column('patient_data', postgresql.JSONB, nullable=False),
        sa.Column('form_data', postgresql.JSONB, nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('denied_at', sa.DateTime(timezone=True)),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.UniqueConstraint('form_number'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by_id'], ['users.id'])
    )
    
    # Create dmerc_attachments table
    op.create_table(
        'dmerc_attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('form_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.ForeignKeyConstraint(['form_id'], ['dmerc_forms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'])
    )
    
    # Create dmerc_history table
    op.create_table(
        'dmerc_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('form_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('changes', postgresql.JSONB, nullable=False),
        sa.Column('performed_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.ForeignKeyConstraint(['form_id'], ['dmerc_forms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performed_by_id'], ['users.id'])
    )
    
    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_organizations_code', 'organizations', ['code'])
    op.create_index('ix_dmerc_forms_form_number', 'dmerc_forms', ['form_number'])
    op.create_index('ix_dmerc_forms_patient_id', 'dmerc_forms', ['patient_id'])


def downgrade() -> None:
    """Drop domain entity tables."""
    # Drop tables
    op.drop_table('dmerc_history')
    op.drop_table('dmerc_attachments')
    op.drop_table('dmerc_forms')
    op.drop_table('user_organizations')
    op.drop_table('organizations')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE dmerc_status')
    op.execute('DROP TYPE dmerc_form_type')
    op.execute('DROP TYPE organization_status')
    op.execute('DROP TYPE organization_type')
    op.execute('DROP TYPE user_status')
    op.execute('DROP TYPE user_role')
