"""
Alembic migration script for creating cmn_request table.
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'cmn_request',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('medicare_mainframe', sa.String(255), nullable=True),
        sa.Column('search_criteria', sa.String(255), nullable=True),
        sa.Column('mock_response', sa.Boolean, nullable=True)
    )

def downgrade():
    op.drop_table('cmn_request')
