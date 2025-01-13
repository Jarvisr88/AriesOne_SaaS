"""Add credentials and audit logging tables.

Revision ID: 003
Revises: 002
Create Date: 2025-01-09 18:52:54.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create credentials and audit logging tables."""
    # Create credential_types enum
    op.execute("""
        CREATE TYPE credential_type AS ENUM (
            'api_key',
            'password',
            'token',
            'certificate',
            'ssh_key',
            'other'
        )
    """)

    # Create credential_status enum
    op.execute("""
        CREATE TYPE credential_status AS ENUM (
            'active',
            'expired',
            'revoked',
            'rotated'
        )
    """)

    # Create credentials table
    op.create_table(
        'credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column(
            'type',
            postgresql.ENUM('api_key', 'password', 'token', 'certificate', 'ssh_key', 'other',
                          name='credential_type'),
            nullable=False
        ),
        sa.Column(
            'status',
            postgresql.ENUM('active', 'expired', 'revoked', 'rotated',
                          name='credential_status'),
            nullable=False,
            server_default='active'
        ),
        sa.Column('encrypted_value', sa.String(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_rotated', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create credential_audit_logs table
    op.create_table(
        'credential_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('credential_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['credential_id'], ['credentials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(
        'ix_credentials_name',
        'credentials',
        ['name'],
        unique=False
    )
    op.create_index(
        'ix_credentials_type',
        'credentials',
        ['type'],
        unique=False
    )
    op.create_index(
        'ix_credentials_status',
        'credentials',
        ['status'],
        unique=False
    )
    op.create_index(
        'ix_credentials_created_by',
        'credentials',
        ['created_by'],
        unique=False
    )
    op.create_index(
        'ix_credential_audit_logs_credential_id',
        'credential_audit_logs',
        ['credential_id'],
        unique=False
    )
    op.create_index(
        'ix_credential_audit_logs_actor_id',
        'credential_audit_logs',
        ['actor_id'],
        unique=False
    )
    op.create_index(
        'ix_credential_audit_logs_created_at',
        'credential_audit_logs',
        ['created_at'],
        unique=False
    )

def downgrade() -> None:
    """Drop credentials and audit logging tables."""
    # Drop indexes
    op.drop_index('ix_credential_audit_logs_created_at', table_name='credential_audit_logs')
    op.drop_index('ix_credential_audit_logs_actor_id', table_name='credential_audit_logs')
    op.drop_index('ix_credential_audit_logs_credential_id', table_name='credential_audit_logs')
    op.drop_index('ix_credentials_created_by', table_name='credentials')
    op.drop_index('ix_credentials_status', table_name='credentials')
    op.drop_index('ix_credentials_type', table_name='credentials')
    op.drop_index('ix_credentials_name', table_name='credentials')

    # Drop tables
    op.drop_table('credential_audit_logs')
    op.drop_table('credentials')

    # Drop enums
    op.execute('DROP TYPE credential_status')
    op.execute('DROP TYPE credential_type')
