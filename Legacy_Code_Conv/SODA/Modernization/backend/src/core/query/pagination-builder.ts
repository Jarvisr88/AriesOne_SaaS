import { injectable } from 'inversify';

@injectable()
export class PaginationBuilder {
  private pageSize: number;
  private pageNumber: number;
  private maxPageSize: number;

  constructor() {
    this.pageSize = 10;
    this.pageNumber = 1;
    this.maxPageSize = 100;
  }

  setPageSize(size: number): this {
    if (size <= 0) {
      throw new Error('Page size must be greater than 0');
    }
    this.pageSize = Math.min(size, this.maxPageSize);
    return this;
  }

  setPageNumber(number: number): this {
    if (number <= 0) {
      throw new Error('Page number must be greater than 0');
    }
    this.pageNumber = number;
    return this;
  }

  setMaxPageSize(size: number): this {
    if (size <= 0) {
      throw new Error('Max page size must be greater than 0');
    }
    this.maxPageSize = size;
    if (this.pageSize > size) {
      this.pageSize = size;
    }
    return this;
  }

  getOffset(): number {
    return (this.pageNumber - 1) * this.pageSize;
  }

  getLimit(): number {
    return this.pageSize;
  }

  getPageMetadata(totalItems: number): PaginationMetadata {
    const totalPages = Math.ceil(totalItems / this.pageSize);

    return {
      pageSize: this.pageSize,
      pageNumber: this.pageNumber,
      totalItems,
      totalPages,
      hasNextPage: this.pageNumber < totalPages,
      hasPreviousPage: this.pageNumber > 1
    };
  }

  validate(): string[] {
    const errors: string[] = [];

    if (this.pageSize <= 0) {
      errors.push('Page size must be greater than 0');
    }

    if (this.pageSize > this.maxPageSize) {
      errors.push(`Page size cannot exceed ${this.maxPageSize}`);
    }

    if (this.pageNumber <= 0) {
      errors.push('Page number must be greater than 0');
    }

    return errors;
  }
}

export interface PaginationMetadata {
  pageSize: number;
  pageNumber: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}
