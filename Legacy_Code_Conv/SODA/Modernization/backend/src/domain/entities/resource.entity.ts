import { Column } from './column.entity';
import { ResourceMetadata } from './resource-metadata.entity';

export class Resource {
  id: string;
  name: string;
  description?: string;
  columns: Column[];
  metadata: ResourceMetadata;
  createdAt: Date;
  updatedAt: Date;
  version: number;

  constructor(data: Partial<Resource>) {
    Object.assign(this, data);
    this.columns = (data.columns || []).map(col => new Column(col));
    this.metadata = new ResourceMetadata(data.metadata || {});
    this.createdAt = new Date(data.createdAt || Date.now());
    this.updatedAt = new Date(data.updatedAt || Date.now());
    this.version = data.version || 1;
  }

  validate(): string[] {
    const errors: string[] = [];

    if (!this.id) {
      errors.push('Resource ID is required');
    }

    if (!this.name) {
      errors.push('Resource name is required');
    }

    if (!this.columns || this.columns.length === 0) {
      errors.push('Resource must have at least one column');
    } else {
      this.columns.forEach((column, index) => {
        const columnErrors = column.validate();
        if (columnErrors.length > 0) {
          errors.push(`Column ${index}: ${columnErrors.join(', ')}`);
        }
      });
    }

    const metadataErrors = this.metadata.validate();
    if (metadataErrors.length > 0) {
      errors.push(`Metadata: ${metadataErrors.join(', ')}`);
    }

    return errors;
  }

  toJSON(): Record<string, any> {
    return {
      id: this.id,
      name: this.name,
      description: this.description,
      columns: this.columns.map(col => col.toJSON()),
      metadata: this.metadata.toJSON(),
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      version: this.version
    };
  }

  update(data: Partial<Resource>): void {
    if (data.name) this.name = data.name;
    if (data.description !== undefined) this.description = data.description;
    if (data.columns) {
      this.columns = data.columns.map(col => new Column(col));
    }
    if (data.metadata) {
      this.metadata.update(data.metadata);
    }
    this.updatedAt = new Date();
    this.version++;
  }

  hasColumn(columnName: string): boolean {
    return this.columns.some(col => col.name === columnName);
  }

  getColumn(columnName: string): Column | undefined {
    return this.columns.find(col => col.name === columnName);
  }

  addColumn(column: Column): void {
    if (this.hasColumn(column.name)) {
      throw new Error(`Column ${column.name} already exists`);
    }
    this.columns.push(new Column(column));
    this.updatedAt = new Date();
    this.version++;
  }

  removeColumn(columnName: string): void {
    const index = this.columns.findIndex(col => col.name === columnName);
    if (index === -1) {
      throw new Error(`Column ${columnName} not found`);
    }
    this.columns.splice(index, 1);
    this.updatedAt = new Date();
    this.version++;
  }

  updateColumn(columnName: string, data: Partial<Column>): void {
    const column = this.getColumn(columnName);
    if (!column) {
      throw new Error(`Column ${columnName} not found`);
    }
    column.update(data);
    this.updatedAt = new Date();
    this.version++;
  }
}
