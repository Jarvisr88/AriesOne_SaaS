"""Reports schema

Revision ID: 001_reports_schema
Revises: None
Create Date: 2025-01-12 12:05:10.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '001_reports_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create categories table
    op.create_table(
        'report_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )
    op.create_index('idx_report_categories_name', 'report_categories', ['name'], unique=True)

    # Create templates table
    op.create_table(
        'report_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('template_type', sa.String(50), nullable=False),  # pdf, excel, csv
        sa.Column('template_data', JSONB, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )
    op.create_index('idx_report_templates_name', 'report_templates', ['name'])
    op.create_index('idx_report_templates_type', 'report_templates', ['template_type'])

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('category_id', UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', UUID(as_uuid=True), nullable=False),
        sa.Column('parameters', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['category_id'], ['report_categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['template_id'], ['report_templates.id'], ondelete='RESTRICT')
    )
    op.create_index('idx_reports_name', 'reports', ['name'])
    op.create_index('idx_reports_category', 'reports', ['category_id'])
    op.create_index('idx_reports_template', 'reports', ['template_id'])
    op.create_index('idx_reports_created_by', 'reports', ['created_by'])

    # Create report_audit table
    op.create_table(
        'report_audit',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('report_id', UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),  # CREATE, UPDATE, DELETE, EXPORT
        sa.Column('changes', JSONB, nullable=False),
        sa.Column('performed_by', UUID(as_uuid=True), nullable=False),
        sa.Column('performed_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE')
    )
    op.create_index('idx_report_audit_report', 'report_audit', ['report_id'])
    op.create_index('idx_report_audit_action', 'report_audit', ['action'])
    op.create_index('idx_report_audit_performed_by', 'report_audit', ['performed_by'])
    op.create_index('idx_report_audit_performed_at', 'report_audit', ['performed_at'])

    # Create audit trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION report_audit_trigger_func()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO report_audit (
                    report_id, action, changes, performed_by
                ) VALUES (
                    NEW.id,
                    'CREATE',
                    jsonb_build_object('new', row_to_json(NEW)::jsonb),
                    NEW.created_by
                );
            ELSIF TG_OP = 'UPDATE' THEN
                INSERT INTO report_audit (
                    report_id, action, changes, performed_by
                ) VALUES (
                    NEW.id,
                    'UPDATE',
                    jsonb_build_object(
                        'old', row_to_json(OLD)::jsonb,
                        'new', row_to_json(NEW)::jsonb,
                        'changed_fields', (
                            SELECT jsonb_object_agg(key, value)
                            FROM jsonb_each(row_to_json(NEW)::jsonb)
                            WHERE row_to_json(NEW)::jsonb->key != row_to_json(OLD)::jsonb->key
                        )
                    ),
                    NEW.updated_by
                );
            ELSIF TG_OP = 'DELETE' THEN
                INSERT INTO report_audit (
                    report_id, action, changes, performed_by
                ) VALUES (
                    OLD.id,
                    'DELETE',
                    jsonb_build_object('old', row_to_json(OLD)::jsonb),
                    current_setting('app.current_user_id')::uuid
                );
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create audit trigger
    op.execute("""
        CREATE TRIGGER report_audit_trigger
        AFTER INSERT OR UPDATE OR DELETE ON reports
        FOR EACH ROW EXECUTE FUNCTION report_audit_trigger_func();
    """)


def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS report_audit_trigger ON reports;")
    
    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS report_audit_trigger_func();")
    
    # Drop tables
    op.drop_table('report_audit')
    op.drop_table('reports')
    op.drop_table('report_templates')
    op.drop_table('report_categories')
