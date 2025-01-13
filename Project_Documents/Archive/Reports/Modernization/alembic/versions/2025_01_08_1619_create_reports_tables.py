"""Create reports tables.

Revision ID: 2025_01_08_1619
Revises: 
Create Date: 2025-01-08 16:19:35.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_01_08_1619'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create reports tables."""
    # Create report_templates table
    op.create_table(
        'report_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_report_templates_category',
        'report_templates',
        ['category'],
        unique=False
    )
    op.create_index(
        'ix_report_templates_file_name',
        'report_templates',
        ['file_name'],
        unique=True
    )
    op.create_index(
        'ix_report_templates_name',
        'report_templates',
        ['name'],
        unique=False
    )

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_reports_category',
        'reports',
        ['category'],
        unique=False
    )
    op.create_index(
        'ix_reports_file_name',
        'reports',
        ['file_name'],
        unique=True
    )
    op.create_index(
        'ix_reports_name',
        'reports',
        ['name'],
        unique=False
    )
    op.create_index(
        'ix_reports_type',
        'reports',
        ['type'],
        unique=False
    )

    # Create report_history table
    op.create_table(
        'report_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_report_history_report_id',
        'report_history',
        ['report_id'],
        unique=False
    )

    # Create report_template_history table
    op.create_table(
        'report_template_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('format', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        'ix_report_template_history_template_id',
        'report_template_history',
        ['template_id'],
        unique=False
    )


def downgrade() -> None:
    """Drop reports tables."""
    op.drop_table('report_template_history')
    op.drop_table('report_history')
    op.drop_table('reports')
    op.drop_table('report_templates')
