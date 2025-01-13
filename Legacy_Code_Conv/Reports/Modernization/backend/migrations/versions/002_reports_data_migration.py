"""Reports data migration

Revision ID: 002_reports_data_migration
Revises: 001_reports_schema
Create Date: 2025-01-12 12:05:20.000000

"""
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '002_reports_data_migration'
down_revision = '001_reports_schema'
branch_labels = None
depends_on = None


def load_xml_reports(filename):
    """Load reports from XML file."""
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        reports = []
        for report in root:
            report_data = {
                'name': report.text,
                'filename': report.get('FileName'),
                'category': report.get('Category'),
                'is_system': bool(int(report.get('System', 0))),
                'is_deleted': bool(int(report.get('Deleted', 0)))
            }
            reports.append(report_data)
        return reports
    except Exception as e:
        print(f"Error loading XML file {filename}: {e}")
        return []


def create_default_template(connection, report_type):
    """Create default template for report type."""
    template_data = {
        'pdf': {
            'format': 'A4',
            'orientation': 'portrait',
            'margins': {'top': 20, 'right': 20, 'bottom': 20, 'left': 20},
            'header': True,
            'footer': True
        },
        'excel': {
            'sheets': [{'name': 'Data', 'freeze_panes': [1, 0]}],
            'header_style': {'bold': True, 'fill': {'color': '#E0E0E0'}},
            'data_style': {'border': True}
        }
    }

    template_id = sa.text("""
        INSERT INTO report_templates (
            name, description, template_type, template_data
        ) VALUES (
            :name, :description, :template_type, :template_data
        ) RETURNING id
    """)
    
    result = connection.execute(
        template_id,
        {
            'name': f'Default {report_type.upper()} Template',
            'description': f'Default template for {report_type} reports',
            'template_type': report_type,
            'template_data': json.dumps(template_data.get(report_type, {}))
        }
    )
    return result.scalar()


def upgrade():
    connection = op.get_bind()
    
    # Create default admin user if not exists
    admin_id = sa.text("SELECT gen_random_uuid()")
    admin_user_id = connection.execute(admin_id).scalar()

    # Create default categories
    categories = {
        'General': 'General purpose reports',
        'Financial': 'Financial reports',
        'Inventory': 'Inventory reports',
        'Sales': 'Sales reports'
    }
    
    for name, description in categories.items():
        category_insert = sa.text("""
            INSERT INTO report_categories (name, description)
            VALUES (:name, :description)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
        """)
        connection.execute(category_insert, {'name': name, 'description': description})

    # Create default templates
    pdf_template_id = create_default_template(connection, 'pdf')
    excel_template_id = create_default_template(connection, 'excel')

    # Load legacy reports
    legacy_dir = os.path.join(os.path.dirname(__file__), '../../../../Legacy_Source_Code/Reports')
    default_reports = load_xml_reports(os.path.join(legacy_dir, 'default_reports.xml'))
    custom_reports = load_xml_reports(os.path.join(legacy_dir, 'custom_reports.xml'))

    # Migrate reports
    for report in default_reports + custom_reports:
        # Get category ID
        category_id = sa.text("""
            SELECT id FROM report_categories
            WHERE name = :category
            LIMIT 1
        """)
        result = connection.execute(
            category_id,
            {'category': report.get('category', 'General')}
        ).scalar()

        # Insert report
        report_insert = sa.text("""
            INSERT INTO reports (
                name, description, category_id, template_id,
                parameters, is_system, is_deleted,
                created_by, updated_by
            ) VALUES (
                :name, :description, :category_id, :template_id,
                :parameters, :is_system, :is_deleted,
                :created_by, :updated_by
            )
        """)
        
        connection.execute(
            report_insert,
            {
                'name': report['name'],
                'description': f"Migrated from {report['filename']}",
                'category_id': result,
                'template_id': pdf_template_id if '.pdf' in report['filename'].lower() else excel_template_id,
                'parameters': json.dumps({'legacy_filename': report['filename']}),
                'is_system': report['is_system'],
                'is_deleted': report['is_deleted'],
                'created_by': admin_user_id,
                'updated_by': admin_user_id
            }
        )


def downgrade():
    connection = op.get_bind()
    
    # Delete migrated reports
    op.execute("DELETE FROM reports WHERE parameters->>'legacy_filename' IS NOT NULL")
    
    # Delete default templates
    op.execute("DELETE FROM report_templates WHERE name LIKE 'Default%'")
    
    # Delete default categories
    op.execute("DELETE FROM report_categories WHERE name IN ('General', 'Financial', 'Inventory', 'Sales')")
