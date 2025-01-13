import { Entity, Column, PrimaryGeneratedColumn, ManyToOne, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { PermissionAction } from '../enums/permission-action.enum';
import { Role } from './role.entity';

@Entity('permissions')
export class Permission {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({
    type: 'enum',
    enum: PermissionAction,
    default: PermissionAction.NONE
  })
  action: PermissionAction;

  @Column()
  resource: string;

  @Column({ type: 'jsonb', nullable: true })
  conditions?: Record<string, any>;

  @ManyToOne(() => Role, role => role.permissions)
  role: Role;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;

  /**
   * Checks if this permission allows a specific action
   */
  can(action: PermissionAction): boolean {
    if (this.action === PermissionAction.ALL) {
      return true;
    }
    if (this.action === PermissionAction.NONE) {
      return false;
    }
    if (this.action === PermissionAction.ADMIN) {
      return true;
    }
    return this.action === action;
  }

  /**
   * Checks if this permission applies to a specific resource
   */
  appliesTo(resource: string): boolean {
    if (this.resource === '*') {
      return true;
    }
    return this.resource === resource || resource.startsWith(`${this.resource}:`);
  }

  /**
   * Evaluates permission conditions against context
   */
  evaluateConditions(context: Record<string, any>): boolean {
    if (!this.conditions) {
      return true;
    }

    return Object.entries(this.conditions).every(([key, value]) => {
      if (typeof value === 'function') {
        return value(context[key]);
      }
      if (Array.isArray(value)) {
        return value.includes(context[key]);
      }
      return context[key] === value;
    });
  }

  /**
   * Creates an empty permission (no access)
   */
  static createEmpty(): Permission {
    const permission = new Permission();
    permission.action = PermissionAction.NONE;
    permission.resource = '*';
    return permission;
  }

  /**
   * Creates a full permission (all access)
   */
  static createFull(): Permission {
    const permission = new Permission();
    permission.action = PermissionAction.ALL;
    permission.resource = '*';
    return permission;
  }

  /**
   * Creates a permission for specific action and resource
   */
  static create(
    action: PermissionAction,
    resource: string,
    conditions?: Record<string, any>
  ): Permission {
    const permission = new Permission();
    permission.action = action;
    permission.resource = resource;
    permission.conditions = conditions;
    return permission;
  }
}
