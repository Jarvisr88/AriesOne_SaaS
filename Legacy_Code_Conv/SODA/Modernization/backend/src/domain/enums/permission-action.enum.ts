/**
 * Represents the different types of actions that can be performed on resources
 */
export enum PermissionAction {
  NONE = 'none',
  VIEW = 'view',
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  PROCESS = 'process',
  ADMIN = 'admin',
  ALL = '*'
}
