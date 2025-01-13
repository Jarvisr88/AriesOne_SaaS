export enum ChangeType {
  MODIFIED = 'modified',
  ADDED = 'added',
  REMOVED = 'removed',
}

export interface FieldChange {
  fieldName: string;
  oldValue: any;
  newValue: any;
  changeType: ChangeType;
  timestamp: string;
  userId?: string;
}
