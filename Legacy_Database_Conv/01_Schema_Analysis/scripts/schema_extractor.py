#!/usr/bin/env python3
"""
Enhanced Schema Extraction Tool
Analyzes SQL schema files and generates structured documentation
"""

import re
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ObjectType(Enum):
    TABLE = "TABLE"
    VIEW = "VIEW"
    PROCEDURE = "PROCEDURE"
    FUNCTION = "FUNCTION"
    TRIGGER = "TRIGGER"

@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool
    default: Optional[str]
    extra: Optional[str]

@dataclass
class ForeignKey:
    columns: List[str]
    ref_database: str
    ref_table: str
    ref_columns: List[str]

@dataclass
class Index:
    name: str
    columns: List[str]
    unique: bool

class SchemaObject:
    def __init__(self, obj_type: ObjectType, name: str, database: str):
        self.type = obj_type
        self.name = name
        self.database = database
        self.definition = ""

class Table(SchemaObject):
    def __init__(self, name: str, database: str):
        super().__init__(ObjectType.TABLE, name, database)
        self.columns: List[Column] = []
        self.primary_key: Optional[List[str]] = None
        self.foreign_keys: List[ForeignKey] = []
        self.indexes: List[Index] = []
        self.engine: Optional[str] = None
        self.charset: Optional[str] = None

class View(SchemaObject):
    def __init__(self, name: str, database: str):
        super().__init__(ObjectType.VIEW, name, database)
        self.dependencies: List[Tuple[str, str]] = []  # [(database, table)]
        self.columns: List[str] = []

class Procedure(SchemaObject):
    def __init__(self, name: str, database: str):
        super().__init__(ObjectType.PROCEDURE, name, database)
        self.parameters: List[Tuple[str, str, str]] = []  # [(name, type, direction)]
        self.body: str = ""
        self.dependencies: List[Tuple[str, str]] = []

class Function(SchemaObject):
    def __init__(self, name: str, database: str):
        super().__init__(ObjectType.FUNCTION, name, database)
        self.parameters: List[Tuple[str, str]] = []  # [(name, type)]
        self.return_type: str = ""
        self.body: str = ""
        self.dependencies: List[Tuple[str, str]] = []

class SchemaExtractor:
    def __init__(self, schema_file: str):
        self.schema_file = schema_file
        self.schema_content = ""
        self.objects: Dict[ObjectType, List[SchemaObject]] = {
            ObjectType.TABLE: [],
            ObjectType.VIEW: [],
            ObjectType.PROCEDURE: [],
            ObjectType.FUNCTION: [],
            ObjectType.TRIGGER: []
        }

    def read_schema(self) -> None:
        with open(self.schema_file, 'r') as f:
            self.schema_content = f.read()

    def _parse_column_definition(self, col_def: str) -> Column:
        """Parse a column definition into structured format with enhanced ENUM handling"""
        # First try to extract ENUM values
        enum_match = re.search(r'ENUM\s*\(\s*([^)]+)\s*\)', col_def, re.IGNORECASE | re.DOTALL)
        if enum_match:
            enum_values = [v.strip().strip("'") for v in enum_match.group(1).split(',')]
            data_type = f"ENUM({', '.join(enum_values)})"
            
            # Now parse the rest of the definition
            name_match = re.match(r'`(\w+)`', col_def)
            if not name_match:
                return None
                
            name = name_match.group(1)
            nullable_match = re.search(r'(NOT\s+NULL|NULL)', col_def, re.IGNORECASE)
            nullable = not bool(nullable_match and nullable_match.group(1) == 'NOT NULL')
            
            default_match = re.search(r'DEFAULT\s+([^,\s]+)', col_def, re.IGNORECASE)
            default = default_match.group(1).strip("'") if default_match else None
            
            extra_match = re.search(r'(?:DEFAULT\s+[^,\s]+\s+)?(.+?)$', col_def)
            extra = extra_match.group(1) if extra_match else None
            
            return Column(name, data_type, nullable, default, extra)
            
        # For non-ENUM columns, use the regular pattern
        pattern = r'`(\w+)`\s+([^,\n]+?)(?:\s+(NOT\s+NULL|NULL))?(?:\s+DEFAULT\s+([^,\s]+))?(?:\s+(.+))?$'
        match = re.match(pattern, col_def.strip(), re.IGNORECASE)
        if not match:
            return None

        name = match.group(1)
        data_type = match.group(2).strip()
        nullable = match.group(3) != 'NOT NULL' if match.group(3) else True
        default = match.group(4)
        extra = match.group(5)

        # Format default value
        if default:
            default = default.strip("'")
            if default.upper() == 'NULL':
                default = None
            elif default.upper() == 'CURRENT_TIMESTAMP':
                default = 'CURRENT_TIMESTAMP'

        # Clean up data type formatting
        data_type = self._format_data_type(data_type)

        return Column(name, data_type, nullable, default, extra)

    def _format_data_type(self, data_type: str) -> str:
        """Format data type for better readability"""
        # Standardize case for common types
        common_types = {
            'INT': 'INT',
            'TINYINT': 'TINYINT',
            'SMALLINT': 'SMALLINT',
            'BIGINT': 'BIGINT',
            'DECIMAL': 'DECIMAL',
            'FLOAT': 'FLOAT',
            'DOUBLE': 'DOUBLE',
            'CHAR': 'CHAR',
            'VARCHAR': 'VARCHAR',
            'TEXT': 'TEXT',
            'MEDIUMTEXT': 'MEDIUMTEXT',
            'LONGTEXT': 'LONGTEXT',
            'DATE': 'DATE',
            'DATETIME': 'DATETIME',
            'TIMESTAMP': 'TIMESTAMP',
            'ENUM': 'ENUM',
            'BOOLEAN': 'BOOLEAN'
        }
        
        # Extract base type and parameters
        base_match = re.match(r'(\w+)(?:\((.*?)\))?', data_type.strip(), re.IGNORECASE)
        if not base_match:
            return data_type
            
        base_type = base_match.group(1).upper()
        params = base_match.group(2)
        
        if base_type in common_types:
            if params:
                return f"{common_types[base_type]}({params})"
            return common_types[base_type]
        
        return data_type

    def _parse_create_table(self, statement: str) -> Table:
        """Enhanced table parsing with better regex patterns"""
        # Extract table name and database
        name_match = re.search(r'CREATE TABLE.*?`(.*?)`\.`(.*?)`', statement, re.DOTALL)
        if not name_match:
            return None

        table = Table(name_match.group(2), name_match.group(1))
        
        # Extract column definitions
        columns_section = re.search(r'\((.*)\)\s*(?:ENGINE|$)', statement, re.DOTALL)
        if not columns_section:
            return None
            
        col_defs = []
        current_def = []
        
        for line in columns_section.group(1).split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith(('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'KEY', 'CONSTRAINT')):
                if current_def:
                    col_defs.append(' '.join(current_def))
                    current_def = []
                continue
                
            if line.endswith(','):
                line = line[:-1]
                
            if line.startswith('`'):
                if current_def:
                    col_defs.append(' '.join(current_def))
                current_def = [line]
            else:
                current_def.append(line)
                
        if current_def:
            col_defs.append(' '.join(current_def))

        # Parse each column definition
        for col_def in col_defs:
            col = self._parse_column_definition(col_def)
            if col:
                table.columns.append(col)

        # Extract primary key
        pk_match = re.search(r'PRIMARY KEY\s*\((.*?)\)', statement)
        if pk_match:
            table.primary_key = [key.strip('` ') for key in pk_match.group(1).split(',')]

        # Extract foreign keys
        fk_pattern = r'CONSTRAINT\s+`?\w+`?\s+FOREIGN KEY\s*\((.*?)\)\s*REFERENCES\s*`(.*?)`\.`(.*?)`\s*\((.*?)\)'
        for fk_match in re.finditer(fk_pattern, statement):
            fk = ForeignKey(
                columns=[col.strip('` ') for col in fk_match.group(1).split(',')],
                ref_database=fk_match.group(2),
                ref_table=fk_match.group(3),
                ref_columns=[col.strip('` ') for col in fk_match.group(4).split(',')]
            )
            table.foreign_keys.append(fk)

        # Extract engine and charset
        engine_match = re.search(r'ENGINE\s*=\s*(\w+)', statement)
        if engine_match:
            table.engine = engine_match.group(1)
            
        charset_match = re.search(r'DEFAULT CHARSET\s*=\s*(\w+)', statement)
        if charset_match:
            table.charset = charset_match.group(1)

        return table

    def _parse_create_view(self, statement: str) -> View:
        """Enhanced view parsing"""
        name_match = re.search(r'CREATE.*?VIEW.*?`(.*?)`\.`(.*?)`', statement)
        if not name_match:
            return None

        view = View(name_match.group(2), name_match.group(1))
        view.definition = statement

        # Extract dependencies with better pattern
        dep_pattern = r'(?:FROM|JOIN)\s+`(.*?)`\.`(.*?)`'
        for dep_match in re.finditer(dep_pattern, statement):
            view.dependencies.append((dep_match.group(1), dep_match.group(2)))

        return view

    def _parse_create_procedure(self, statement: str) -> Procedure:
        """Parse CREATE PROCEDURE statements"""
        name_match = re.search(r'CREATE.*?PROCEDURE.*?`(.*?)`\.`(.*?)`', statement)
        if not name_match:
            return None

        proc = Procedure(name_match.group(2), name_match.group(1))
        
        # Extract parameters
        param_pattern = r'(?:IN|OUT|INOUT)\s+(\w+)\s+([^,\s]+)'
        for param_match in re.finditer(param_pattern, statement):
            proc.parameters.append((
                param_match.group(1),
                param_match.group(2),
                param_match.group(0).split()[0]
            ))

        # Extract body
        body_match = re.search(r'BEGIN(.*?)END', statement, re.DOTALL)
        if body_match:
            proc.body = body_match.group(1).strip()

        return proc

    def _parse_create_function(self, statement: str) -> Function:
        """Parse CREATE FUNCTION statements"""
        name_match = re.search(r'CREATE.*?FUNCTION.*?`(.*?)`\.`(.*?)`', statement)
        if not name_match:
            return None

        func = Function(name_match.group(2), name_match.group(1))

        # Extract return type
        returns_match = re.search(r'RETURNS\s+([^\s]+)', statement)
        if returns_match:
            func.return_type = returns_match.group(1)

        # Extract parameters
        param_pattern = r'(\w+)\s+([^,\s]+)'
        params_section = re.search(r'\((.*?)\)', statement)
        if params_section:
            for param_match in re.finditer(param_pattern, params_section.group(1)):
                func.parameters.append((param_match.group(1), param_match.group(2)))

        # Extract body
        body_match = re.search(r'BEGIN(.*?)END', statement, re.DOTALL)
        if body_match:
            func.body = body_match.group(1).strip()

        return func

    def _generate_domain_diagram(self, domain_name: str, tables: List[Table]) -> str:
        """Generate an enhanced relationship diagram for a specific domain"""
        if not tables:
            return f"""```mermaid
erDiagram
    %% {domain_name.upper()} Domain
    %% No tables found for this domain
```"""

        diagram = [
            "```mermaid",
            "erDiagram",
            f"    %% {domain_name.upper()} Domain"
        ]

        # Create a mapping of table names to tables for easier lookup
        table_map = {table.name.lower().replace('tbl_', ''): table for table in tables}

        # Add tables with key columns
        for table_name, table in table_map.items():
            diagram.append(f"    {table.name} {{")
            
            # Add primary key columns
            if table.primary_key:
                for col in table.columns:
                    if col.name in table.primary_key:
                        diagram.append(f"        PK {col.data_type} {col.name}")
            
            # Add foreign key columns
            fk_columns = set()
            for fk in table.foreign_keys:
                for col in fk.columns:
                    fk_columns.add(col)
            
            for col in table.columns:
                if col.name in fk_columns:
                    diagram.append(f"        FK {col.data_type} {col.name}")
            
            # Add other important columns (limited to keep diagram readable)
            important_columns = ['name', 'code', 'type', 'status', 'date', 'active', 'description']
            for col in table.columns:
                if (col.name.lower() in important_columns or 
                    any(key in col.name.lower() for key in important_columns)):
                    if col.name not in fk_columns and col.name not in (table.primary_key or []):
                        diagram.append(f"        {col.data_type} {col.name}")
            
            diagram.append("    }")

        # Add relationships with proper cardinality
        for table_name, table in table_map.items():
            for fk in table.foreign_keys:
                ref_table = fk.ref_table.lower().replace('tbl_', '')
                if ref_table in table_map:
                    # Determine cardinality based on nullable and unique constraints
                    left_card = "||"  # one
                    right_card = "o{" if any(col for col in table.columns 
                                           if col.name in fk.columns and col.nullable) else "||"
                    
                    diagram.append(f"    {table.name} {left_card}--{right_card} {fk.ref_table} : references")

        diagram.append("```")
        return "\n".join(diagram)

    def _generate_mermaid_diagram(self, tables: List[Table], output_dir: str) -> None:
        """Generate improved relationship diagrams"""
        # Define business domains with their tables
        domains = {
            "customer": ["tbl_customer", "customer_insurance", "customer_notes", "customertype", "customerclass"],
            "order": ["tbl_order", "orderdetails", "order_survey", "orderdeposits"],
            "inventory": ["tbl_inventory", "inventoryitem", "serial", "warehouse", "kit", "kitdetails"],
            "medical": ["tbl_cmnform", "doctor", "facility", "referral", "icd9", "icd10"],
            "billing": ["tbl_invoice", "invoicedetails", "payment", "paymentplan", "batchpayment"]
        }

        # Generate main relationship diagram (limited to core tables)
        core_tables = []
        core_table_names = set()
        for domain_tables in domains.values():
            core_table_names.update(domain_tables[:2])  # Take only the first 2 tables from each domain
        
        core_tables = [table for table in tables if table.name.lower() in 
                      [name.lower() for name in core_table_names]]
        if core_tables:
            main_diagram = self._generate_domain_diagram("core", core_tables)
            with open(f"{output_dir}/relationships_core.md", 'w') as f:
                f.write(main_diagram)

        # Generate domain-specific diagrams
        for domain, table_names in domains.items():
            domain_tables = [table for table in tables if table.name.lower() in 
                           [name.lower() for name in table_names]]
            if domain_tables:
                domain_diagram = self._generate_domain_diagram(domain, domain_tables)
                with open(f"{output_dir}/relationships_{domain}.md", 'w') as f:
                    f.write(domain_diagram)

    def _generate_table_doc(self, table: Table, output_dir: str) -> None:
        """Generate markdown documentation for a table"""
        doc = f"# Table: {table.name}\n\n"
        doc += f"**Database:** {table.database}\n\n"

        # Columns
        doc += "## Columns\n\n"
        doc += "| Column | Data Type | Nullable | Default | Extra |\n"
        doc += "|--------|-----------|----------|---------|-------|\n"
        for col in table.columns:
            doc += f"| {col.name} | {col.data_type} | {col.nullable} | {col.default} | {col.extra} |\n"

        # Primary Key
        if table.primary_key:
            doc += f"\n## Primary Key\n"
            doc += f"- {', '.join(table.primary_key)}\n"

        # Foreign Keys
        if table.foreign_keys:
            doc += f"\n## Foreign Keys\n"
            for fk in table.foreign_keys:
                doc += f"- {', '.join(fk.columns)} → {fk.ref_database}.{fk.ref_table} ({', '.join(fk.ref_columns)})\n"

        # Engine and Charset
        if table.engine:
            doc += f"\n## Engine\n"
            doc += f"- {table.engine}\n"
        if table.charset:
            doc += f"\n## Charset\n"
            doc += f"- {table.charset}\n"

        # Write to file
        filename = f"{output_dir}/{table.database}_{table.name}.md"
        with open(filename, 'w') as f:
            f.write(doc)

    def _generate_view_doc(self, view: View, output_dir: str) -> None:
        """Generate markdown documentation for a view"""
        doc = f"# View: {view.name}\n\n"
        doc += f"**Database:** {view.database}\n\n"

        # Dependencies
        if view.dependencies:
            doc += "## Dependencies\n\n"
            for dep in view.dependencies:
                doc += f"- {dep[0]}.{dep[1]}\n"

        # Definition
        doc += "\n## Definition\n\n```sql\n"
        doc += view.definition
        doc += "\n```\n"

        # Write to file
        filename = f"{output_dir}/{view.database}_{view.name}.md"
        with open(filename, 'w') as f:
            f.write(doc)

    def _generate_procedure_doc(self, proc: Procedure, output_dir: str) -> None:
        """Generate markdown documentation for a procedure"""
        doc = f"# Procedure: {proc.name}\n\n"
        doc += f"**Database:** {proc.database}\n\n"

        # Parameters
        if proc.parameters:
            doc += "## Parameters\n\n"
            for param in proc.parameters:
                doc += f"- {param[0]} ({param[1]}) {param[2]}\n"

        # Body
        doc += "\n## Body\n\n```sql\n"
        doc += proc.body
        doc += "\n```\n"

        # Write to file
        filename = f"{output_dir}/{proc.database}_{proc.name}.md"
        with open(filename, 'w') as f:
            f.write(doc)

    def _generate_function_doc(self, func: Function, output_dir: str) -> None:
        """Generate markdown documentation for a function"""
        doc = f"# Function: {func.name}\n\n"
        doc += f"**Database:** {func.database}\n\n"

        # Parameters
        if func.parameters:
            doc += "## Parameters\n\n"
            for param in func.parameters:
                doc += f"- {param[0]} ({param[1]})\n"

        # Return Type
        if func.return_type:
            doc += f"\n## Return Type\n"
            doc += f"- {func.return_type}\n"

        # Body
        doc += "\n## Body\n\n```sql\n"
        doc += func.body
        doc += "\n```\n"

        # Write to file
        filename = f"{output_dir}/{func.database}_{func.name}.md"
        with open(filename, 'w') as f:
            f.write(doc)

    def generate_documentation(self, output_dir: str) -> None:
        """Generate enhanced documentation"""
        os.makedirs(output_dir, exist_ok=True)

        # Parse schema
        self._parse_schema()

        # Generate documentation for each object type
        for obj_type, objects in self.objects.items():
            for obj in objects:
                if isinstance(obj, Table):
                    self._generate_table_doc(obj, output_dir)
                elif isinstance(obj, View):
                    self._generate_view_doc(obj, output_dir)
                elif isinstance(obj, Procedure):
                    self._generate_procedure_doc(obj, output_dir)
                elif isinstance(obj, Function):
                    self._generate_function_doc(obj, output_dir)

        # Generate relationship diagrams
        self._generate_mermaid_diagram(
            [obj for obj in self.objects[ObjectType.TABLE] if isinstance(obj, Table)],
            output_dir
        )

    def _parse_schema(self) -> None:
        """Parse the schema content"""
        # Extract CREATE statements
        create_pattern = r'(?:CREATE TABLE|CREATE VIEW|CREATE PROCEDURE|CREATE FUNCTION).*?(?=CREATE|$)'
        creates = re.finditer(create_pattern, self.schema_content, re.DOTALL | re.IGNORECASE)

        # Parse each CREATE statement
        for create in creates:
            statement = create.group()
            if statement.upper().startswith('CREATE TABLE'):
                table = self._parse_create_table(statement)
                if table:
                    self.objects[ObjectType.TABLE].append(table)
            elif statement.upper().startswith('CREATE VIEW'):
                view = self._parse_create_view(statement)
                if view:
                    self.objects[ObjectType.VIEW].append(view)
            elif statement.upper().startswith('CREATE PROCEDURE'):
                proc = self._parse_create_procedure(statement)
                if proc:
                    self.objects[ObjectType.PROCEDURE].append(proc)
            elif statement.upper().startswith('CREATE FUNCTION'):
                func = self._parse_create_function(statement)
                if func:
                    self.objects[ObjectType.FUNCTION].append(func)

def main():
    """Main function to run the schema extractor"""
    schema_file = "/home/ob-1/Project/AriesOne_SaaS/Legacy_Database_Source/Schema/DMEWorks_schema.sql"
    output_dir = "/home/ob-1/Project/AriesOne_SaaS/Legacy_Database_Conv/01_Schema_Analysis/generated_docs"
    
    print(f"Starting enhanced schema extraction from {schema_file}")
    extractor = SchemaExtractor(schema_file)
    
    print("Reading schema file...")
    extractor.read_schema()
    
    print("Generating enhanced documentation...")
    extractor.generate_documentation(output_dir)
    
    print(f"Documentation generated in {output_dir}")

if __name__ == "__main__":
    main()
