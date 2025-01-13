"""
Initial Database Migration
Version: 1.0.0
Last Updated: 2025-01-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create tenant table
    op.create_table(
        'tenant',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('contact_name', sa.String(length=100), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('subscription_plan', sa.String(length=50), 
                 server_default='free', nullable=False),
        sa.Column('subscription_start', sa.DateTime(), nullable=True),
        sa.Column('subscription_end', sa.DateTime(), nullable=True),
        sa.Column('settings', postgresql.JSONB(), server_default='{}', nullable=False),
        sa.Column('theme', sa.String(length=50), server_default='default', nullable=True),
        sa.Column('timezone', sa.String(length=50), server_default='UTC', nullable=False),
        sa.Column('max_users', sa.Integer(), server_default='10', nullable=False),
        sa.Column('max_storage', sa.BigInteger(), 
                 server_default='1073741824', nullable=False),
        sa.Column('used_storage', sa.BigInteger(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_tenant')),
        sa.UniqueConstraint('slug', name=op.f('uq_tenant_slug'))
    )
    op.create_index(op.f('ix_tenant_slug'), 'tenant', ['slug'], unique=True)
    
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False),
        sa.Column('mfa_secret', sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], 
                              name=op.f('fk_user_tenant_id_tenant'),
                              ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('email', name=op.f('uq_user_email'))
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_tenant_id'), 'user', ['tenant_id'], unique=False)
    
    # Create user_profile table
    op.create_table(
        'userprofile',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('language', sa.String(length=10), 
                 server_default='en', nullable=False),
        sa.Column('timezone', sa.String(length=50), 
                 server_default='UTC', nullable=False),
        sa.Column('theme', sa.String(length=20), 
                 server_default='light', nullable=False),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], 
                              name=op.f('fk_userprofile_user_id_user'),
                              ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_userprofile')),
        sa.UniqueConstraint('user_id', name=op.f('uq_userprofile_user_id'))
    )
    
    # Create user_role table
    op.create_table(
        'userrole',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_name', sa.String(length=50), nullable=False),
        sa.Column('permissions', postgresql.JSONB(), 
                 server_default='[]', nullable=False),
        sa.Column('scope', sa.String(length=50), 
                 server_default='tenant', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], 
                              name=op.f('fk_userrole_user_id_user'),
                              ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_userrole'))
    )
    op.create_index(op.f('ix_userrole_user_id'), 
                   'userrole', ['user_id'], unique=False)
    
    # Create user_session table
    op.create_table(
        'usersession',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('device_info', postgresql.JSONB(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revocation_reason', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], 
                              name=op.f('fk_usersession_user_id_user'),
                              ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_usersession')),
        sa.UniqueConstraint('token', name=op.f('uq_usersession_token'))
    )
    op.create_index(op.f('ix_usersession_token'), 
                   'usersession', ['token'], unique=True)
    op.create_index(op.f('ix_usersession_user_id'), 
                   'usersession', ['user_id'], unique=False)
    
    # Create audit_log table
    op.create_table(
        'auditlog',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('correlation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), 
                 server_default='{}', nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], 
                              name=op.f('fk_auditlog_tenant_id_tenant'),
                              ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], 
                              name=op.f('fk_auditlog_user_id_user'),
                              ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_auditlog'))
    )
    op.create_index(op.f('ix_auditlog_correlation_id'), 
                   'auditlog', ['correlation_id'], unique=False)
    op.create_index(op.f('ix_auditlog_entity_id'), 
                   'auditlog', ['entity_id'], unique=False)
    op.create_index(op.f('ix_auditlog_entity_type'), 
                   'auditlog', ['entity_type'], unique=False)
    op.create_index(op.f('ix_auditlog_event_type'), 
                   'auditlog', ['event_type'], unique=False)
    op.create_index(op.f('ix_auditlog_tenant_id'), 
                   'auditlog', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_auditlog_user_id'), 
                   'auditlog', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_table('auditlog')
    op.drop_table('usersession')
    op.drop_table('userrole')
    op.drop_table('userprofile')
    op.drop_table('user')
    op.drop_table('tenant')
