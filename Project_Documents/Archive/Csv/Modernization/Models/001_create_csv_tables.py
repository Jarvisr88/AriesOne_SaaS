"""create csv tables

Revision ID: 001
Revises: 
Create Date: 2025-01-07 16:16:30.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create csv_imports table
    op.create_table(
        'csv_imports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('import_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('headers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_csv_imports_id'), 'csv_imports', ['id'], unique=False)

    # Create csv_import_errors table
    op.create_table(
        'csv_import_errors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('import_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('field_index', sa.Integer(), nullable=True),
        sa.Column('raw_data', sa.String(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['import_id'], ['csv_imports.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_csv_import_errors_id'), 'csv_import_errors', ['id'], unique=False)
    op.create_index(op.f('ix_csv_import_errors_import_id'), 'csv_import_errors', ['import_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_csv_import_errors_import_id'), table_name='csv_import_errors')
    op.drop_index(op.f('ix_csv_import_errors_id'), table_name='csv_import_errors')
    op.drop_table('csv_import_errors')
    op.drop_index(op.f('ix_csv_imports_id'), table_name='csv_imports')
    op.drop_table('csv_imports')
