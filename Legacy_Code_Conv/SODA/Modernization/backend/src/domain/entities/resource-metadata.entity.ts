export class ResourceMetadata {
  owner: string;
  createdAt: Date;
  updatedAt: Date;
  license?: string;
  tags: string[];
  category?: string;
  attribution?: string;
  description?: string;
  rowCount: number;
  viewCount: number;
  downloadCount: number;
  isPublic: boolean;
  version: number;
  sourceUrl?: string;
  contactEmail?: string;
  lastSync?: Date;
  refreshFrequency?: string;
  customFields: Record<string, any>;

  constructor(data: Partial<ResourceMetadata>) {
    Object.assign(this, {
      tags: [],
      rowCount: 0,
      viewCount: 0,
      downloadCount: 0,
      isPublic: false,
      version: 1,
      customFields: {},
      ...data
    });

    this.createdAt = new Date(data.createdAt || Date.now());
    this.updatedAt = new Date(data.updatedAt || Date.now());
    if (data.lastSync) {
      this.lastSync = new Date(data.lastSync);
    }
  }

  validate(): string[] {
    const errors: string[] = [];

    if (!this.owner) {
      errors.push('Owner is required');
    }

    if (this.contactEmail && !this.validateEmail(this.contactEmail)) {
      errors.push('Invalid contact email');
    }

    if (this.sourceUrl && !this.validateUrl(this.sourceUrl)) {
      errors.push('Invalid source URL');
    }

    if (this.refreshFrequency && !this.validateRefreshFrequency(this.refreshFrequency)) {
      errors.push('Invalid refresh frequency');
    }

    return errors;
  }

  private validateEmail(email: string): boolean {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
  }

  private validateUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  private validateRefreshFrequency(frequency: string): boolean {
    const validFrequencies = ['hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never'];
    return validFrequencies.includes(frequency.toLowerCase());
  }

  toJSON(): Record<string, any> {
    return {
      owner: this.owner,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString(),
      license: this.license,
      tags: this.tags,
      category: this.category,
      attribution: this.attribution,
      description: this.description,
      rowCount: this.rowCount,
      viewCount: this.viewCount,
      downloadCount: this.downloadCount,
      isPublic: this.isPublic,
      version: this.version,
      sourceUrl: this.sourceUrl,
      contactEmail: this.contactEmail,
      lastSync: this.lastSync?.toISOString(),
      refreshFrequency: this.refreshFrequency,
      customFields: this.customFields
    };
  }

  update(data: Partial<ResourceMetadata>): void {
    const oldData = { ...this };
    Object.assign(this, data);
    this.updatedAt = new Date();
    this.version++;

    // Restore Date objects if they were overwritten
    if (data.createdAt) {
      this.createdAt = new Date(data.createdAt);
    } else {
      this.createdAt = oldData.createdAt;
    }

    if (data.lastSync) {
      this.lastSync = new Date(data.lastSync);
    }
  }

  incrementViewCount(): void {
    this.viewCount++;
    this.updatedAt = new Date();
  }

  incrementDownloadCount(): void {
    this.downloadCount++;
    this.updatedAt = new Date();
  }

  updateRowCount(count: number): void {
    this.rowCount = count;
    this.updatedAt = new Date();
  }

  addTag(tag: string): void {
    if (!this.tags.includes(tag)) {
      this.tags.push(tag);
      this.updatedAt = new Date();
    }
  }

  removeTag(tag: string): void {
    const index = this.tags.indexOf(tag);
    if (index !== -1) {
      this.tags.splice(index, 1);
      this.updatedAt = new Date();
    }
  }

  setCustomField(key: string, value: any): void {
    this.customFields[key] = value;
    this.updatedAt = new Date();
  }

  getCustomField(key: string): any {
    return this.customFields[key];
  }

  removeCustomField(key: string): void {
    delete this.customFields[key];
    this.updatedAt = new Date();
  }

  clone(): ResourceMetadata {
    return new ResourceMetadata(this.toJSON());
  }
}
