"""
Alembic migration script for creating cmn_request_search_criteria table.
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'cmn_request_search_criteria',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('npi', sa.String(255), nullable=True),
        sa.Column('hic', sa.String(255), nullable=True),
        sa.Column('hcpcs', sa.String(255), nullable=True),
        sa.Column('mbi', sa.String(255), nullable=True),
        sa.Column('max_results', sa.Integer, nullable=True)
    )

def downgrade():
    op.drop_table('cmn_request_search_criteria')
