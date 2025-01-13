import { injectable } from 'inversify';
import { WhereClause } from '../../domain/dtos/resource.dto';
import { Column } from '../../domain/entities/column.entity';
import { DataType } from '../../domain/enums/data-type.enum';

@injectable()
export class FilterBuilder {
  private column: Column;
  private field: string;

  setColumn(column: Column): this {
    this.column = column;
    this.field = column.name;
    return this;
  }

  equals(value: any): WhereClause {
    return {
      field: this.field,
      operator: 'EQ',
      value
    };
  }

  notEquals(value: any): WhereClause {
    return {
      field: this.field,
      operator: 'NEQ',
      value
    };
  }

  greaterThan(value: number | Date): WhereClause {
    this.validateNumericOrDate();
    return {
      field: this.field,
      operator: 'GT',
      value
    };
  }

  greaterThanOrEqual(value: number | Date): WhereClause {
    this.validateNumericOrDate();
    return {
      field: this.field,
      operator: 'GTE',
      value
    };
  }

  lessThan(value: number | Date): WhereClause {
    this.validateNumericOrDate();
    return {
      field: this.field,
      operator: 'LT',
      value
    };
  }

  lessThanOrEqual(value: number | Date): WhereClause {
    this.validateNumericOrDate();
    return {
      field: this.field,
      operator: 'LTE',
      value
    };
  }

  between(start: number | Date, end: number | Date): WhereClause {
    this.validateNumericOrDate();
    return {
      field: this.field,
      operator: 'BETWEEN',
      value: [start, end]
    };
  }

  in(values: any[]): WhereClause {
    return {
      field: this.field,
      operator: 'IN',
      value: values
    };
  }

  like(pattern: string): WhereClause {
    this.validateText();
    return {
      field: this.field,
      operator: 'LIKE',
      value: pattern
    };
  }

  ilike(pattern: string): WhereClause {
    this.validateText();
    return {
      field: this.field,
      operator: 'ILIKE',
      value: pattern
    };
  }

  isNull(): WhereClause {
    return {
      field: this.field,
      operator: 'IS NULL',
      value: null
    };
  }

  isNotNull(): WhereClause {
    return {
      field: this.field,
      operator: 'IS NOT NULL',
      value: null
    };
  }

  withinCircle(latitude: number, longitude: number, radius: number): WhereClause {
    this.validateLocation();
    return {
      field: this.field,
      operator: 'WITHIN_CIRCLE',
      value: { latitude, longitude, radius }
    };
  }

  withinBox(
    minLatitude: number,
    minLongitude: number,
    maxLatitude: number,
    maxLongitude: number
  ): WhereClause {
    this.validateLocation();
    return {
      field: this.field,
      operator: 'WITHIN_BOX',
      value: {
        minLatitude,
        minLongitude,
        maxLatitude,
        maxLongitude
      }
    };
  }

  private validateNumericOrDate(): void {
    if (this.column.dataType !== DataType.NUMBER && this.column.dataType !== DataType.DATE) {
      throw new Error(`Column ${this.field} must be numeric or date type for this operation`);
    }
  }

  private validateText(): void {
    if (
      this.column.dataType !== DataType.TEXT &&
      this.column.dataType !== DataType.URL &&
      this.column.dataType !== DataType.PHONE
    ) {
      throw new Error(`Column ${this.field} must be text type for this operation`);
    }
  }

  private validateLocation(): void {
    if (this.column.dataType !== DataType.LOCATION) {
      throw new Error(`Column ${this.field} must be location type for this operation`);
    }
  }
}
