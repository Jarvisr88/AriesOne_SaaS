import { injectable } from 'inversify';
import { WhereClause, OrderByClause } from '../../domain/dtos/resource.dto';
import { DataType } from '../../domain/enums/data-type.enum';
import { Column } from '../../domain/entities/column.entity';

@injectable()
export class SoqlQueryBuilder {
  private selectClauses: string[] = [];
  private whereClauses: WhereClause[] = [];
  private orderByClauses: OrderByClause[] = [];
  private limitValue?: number;
  private offsetValue?: number;
  private columns: Map<string, Column> = new Map();

  constructor() {
    this.reset();
  }

  reset(): this {
    this.selectClauses = [];
    this.whereClauses = [];
    this.orderByClauses = [];
    this.limitValue = undefined;
    this.offsetValue = undefined;
    this.columns = new Map();
    return this;
  }

  setColumns(columns: Column[]): this {
    this.columns = new Map(columns.map(col => [col.name, col]));
    return this;
  }

  select(columns: string[]): this {
    this.selectClauses = columns;
    return this;
  }

  where(clause: WhereClause): this {
    this.whereClauses.push(clause);
    return this;
  }

  orderBy(field: string, direction: 'ASC' | 'DESC'): this {
    this.orderByClauses.push({ field, direction });
    return this;
  }

  limit(value: number): this {
    this.limitValue = value;
    return this;
  }

  offset(value: number): this {
    this.offsetValue = value;
    return this;
  }

  private formatValue(value: any, column?: Column): string {
    if (value === null) return 'null';
    if (value === undefined) return 'null';

    if (!column) return JSON.stringify(value);

    switch (column.dataType) {
      case DataType.TEXT:
      case DataType.URL:
      case DataType.PHONE:
        return `'${value.replace(/'/g, "''")}'`;

      case DataType.NUMBER:
        return value.toString();

      case DataType.BOOLEAN:
        return value ? 'true' : 'false';

      case DataType.DATE:
        if (value instanceof Date) {
          return `'${value.toISOString()}'`;
        }
        return `'${new Date(value).toISOString()}'`;

      case DataType.LOCATION:
        return `'POINT(${value.longitude} ${value.latitude})'`;

      case DataType.JSON:
        return `'${JSON.stringify(value).replace(/'/g, "''")}'`;

      default:
        return JSON.stringify(value);
    }
  }

  private buildSelectClause(): string {
    if (this.selectClauses.length === 0) {
      return '*';
    }
    return this.selectClauses.join(', ');
  }

  private buildWhereClause(): string {
    if (this.whereClauses.length === 0) {
      return '';
    }

    const conditions = this.whereClauses.map(clause => {
      const column = this.columns.get(clause.field);
      const value = this.formatValue(clause.value, column);

      switch (clause.operator.toUpperCase()) {
        case 'EQ':
          return `${clause.field} = ${value}`;
        case 'NEQ':
          return `${clause.field} != ${value}`;
        case 'GT':
          return `${clause.field} > ${value}`;
        case 'GTE':
          return `${clause.field} >= ${value}`;
        case 'LT':
          return `${clause.field} < ${value}`;
        case 'LTE':
          return `${clause.field} <= ${value}`;
        case 'IN':
          const values = Array.isArray(clause.value)
            ? clause.value.map(v => this.formatValue(v, column)).join(', ')
            : value;
          return `${clause.field} IN (${values})`;
        case 'BETWEEN':
          const [start, end] = clause.value;
          return `${clause.field} BETWEEN ${this.formatValue(start, column)} AND ${this.formatValue(end, column)}`;
        case 'LIKE':
          return `${clause.field} LIKE ${value}`;
        case 'ILIKE':
          return `${clause.field} ILIKE ${value}`;
        case 'IS NULL':
          return `${clause.field} IS NULL`;
        case 'IS NOT NULL':
          return `${clause.field} IS NOT NULL`;
        default:
          throw new Error(`Unsupported operator: ${clause.operator}`);
      }
    });

    return `WHERE ${conditions.join(' AND ')}`;
  }

  private buildOrderByClause(): string {
    if (this.orderByClauses.length === 0) {
      return '';
    }

    const orderBy = this.orderByClauses
      .map(clause => `${clause.field} ${clause.direction}`)
      .join(', ');

    return `ORDER BY ${orderBy}`;
  }

  private buildLimitClause(): string {
    if (this.limitValue === undefined) {
      return '';
    }
    return `LIMIT ${this.limitValue}`;
  }

  private buildOffsetClause(): string {
    if (this.offsetValue === undefined) {
      return '';
    }
    return `OFFSET ${this.offsetValue}`;
  }

  build(): string {
    const clauses = [
      'SELECT',
      this.buildSelectClause(),
      this.buildWhereClause(),
      this.buildOrderByClause(),
      this.buildLimitClause(),
      this.buildOffsetClause()
    ];

    return clauses.filter(clause => clause).join(' ');
  }

  validate(): string[] {
    const errors: string[] = [];

    // Validate select clauses
    if (this.selectClauses.length > 0) {
      for (const column of this.selectClauses) {
        if (!this.columns.has(column)) {
          errors.push(`Selected column '${column}' does not exist`);
        }
      }
    }

    // Validate where clauses
    for (const clause of this.whereClauses) {
      const column = this.columns.get(clause.field);
      if (!column) {
        errors.push(`Where clause field '${clause.field}' does not exist`);
        continue;
      }

      // Validate operator
      const validOperators = this.getValidOperators(column.dataType);
      if (!validOperators.includes(clause.operator.toUpperCase())) {
        errors.push(`Invalid operator '${clause.operator}' for column type ${column.dataType}`);
      }

      // Validate value type
      const valueError = this.validateValueType(clause.value, column);
      if (valueError) {
        errors.push(valueError);
      }
    }

    // Validate order by clauses
    for (const clause of this.orderByClauses) {
      if (!this.columns.has(clause.field)) {
        errors.push(`Order by field '${clause.field}' does not exist`);
      }
    }

    // Validate limit and offset
    if (this.limitValue !== undefined && this.limitValue <= 0) {
      errors.push('Limit must be greater than 0');
    }

    if (this.offsetValue !== undefined && this.offsetValue < 0) {
      errors.push('Offset must be non-negative');
    }

    return errors;
  }

  private getValidOperators(dataType: DataType): string[] {
    const commonOperators = ['EQ', 'NEQ', 'IN', 'IS NULL', 'IS NOT NULL'];

    switch (dataType) {
      case DataType.TEXT:
      case DataType.URL:
      case DataType.PHONE:
        return [...commonOperators, 'LIKE', 'ILIKE'];

      case DataType.NUMBER:
      case DataType.DATE:
        return [...commonOperators, 'GT', 'GTE', 'LT', 'LTE', 'BETWEEN'];

      case DataType.BOOLEAN:
        return ['EQ', 'NEQ', 'IS NULL', 'IS NOT NULL'];

      case DataType.LOCATION:
        return [...commonOperators, 'WITHIN_CIRCLE', 'WITHIN_BOX'];

      default:
        return commonOperators;
    }
  }

  private validateValueType(value: any, column: Column): string | null {
    if (value === null || value === undefined) {
      return null;
    }

    switch (column.dataType) {
      case DataType.NUMBER:
        if (typeof value !== 'number') {
          return `Value for column '${column.name}' must be a number`;
        }
        break;

      case DataType.BOOLEAN:
        if (typeof value !== 'boolean') {
          return `Value for column '${column.name}' must be a boolean`;
        }
        break;

      case DataType.DATE:
        if (!(value instanceof Date) && isNaN(Date.parse(value))) {
          return `Value for column '${column.name}' must be a valid date`;
        }
        break;

      case DataType.LOCATION:
        if (!value.latitude || !value.longitude) {
          return `Value for column '${column.name}' must be a valid location object`;
        }
        break;
    }

    return null;
  }
}
