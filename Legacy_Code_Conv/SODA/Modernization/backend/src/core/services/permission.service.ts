import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Permission } from '../../domain/entities/permission.entity';
import { Role } from '../../domain/entities/role.entity';
import { User } from '../../domain/entities/user.entity';
import { PermissionAction } from '../../domain/enums/permission-action.enum';
import { CacheService } from '../cache/cache.service';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';
import { AuditService } from './audit.service';
import { NotFoundError, UnauthorizedError } from '../errors';

@Injectable()
export class PermissionService {
  private readonly CACHE_TTL = 300; // 5 minutes
  private readonly CACHE_PREFIX = 'permissions:';

  constructor(
    @InjectRepository(Permission)
    private readonly permissionRepository: Repository<Permission>,
    @InjectRepository(Role)
    private readonly roleRepository: Repository<Role>,
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly cacheService: CacheService,
    private readonly configService: ConfigService,
    private readonly logger: LoggerService,
    private readonly auditService: AuditService
  ) {}

  /**
   * Checks if a user has permission to perform an action on a resource
   */
  async checkPermission(
    userId: string,
    action: PermissionAction,
    resource: string,
    context: Record<string, any> = {}
  ): Promise<boolean> {
    this.logger.debug('Checking permission', { userId, action, resource });

    // Check cache first
    const cacheKey = this.getCacheKey(userId, action, resource);
    const cachedResult = await this.cacheService.get<boolean>(cacheKey);
    if (cachedResult !== null) {
      return cachedResult;
    }

    // Get user with roles
    const user = await this.userRepository.findOne({
      where: { id: userId },
      relations: ['roles', 'roles.permissions']
    });

    if (!user) {
      throw new NotFoundError(`User not found: ${userId}`);
    }

    // Check permissions across all roles
    const hasPermission = user.roles.some(role =>
      role.permissions.some(permission =>
        permission.can(action) &&
        permission.appliesTo(resource) &&
        permission.evaluateConditions({ ...context, user })
      )
    );

    // Audit the permission check
    await this.auditService.logPermissionCheck({
      userId,
      action,
      resource,
      context,
      allowed: hasPermission
    });

    // Cache the result
    await this.cacheService.set(cacheKey, hasPermission, this.CACHE_TTL);

    return hasPermission;
  }

  /**
   * Ensures a user has permission, throws if not
   */
  async ensurePermission(
    userId: string,
    action: PermissionAction,
    resource: string,
    context: Record<string, any> = {}
  ): Promise<void> {
    const hasPermission = await this.checkPermission(
      userId,
      action,
      resource,
      context
    );

    if (!hasPermission) {
      throw new UnauthorizedError(
        `User ${userId} does not have permission to ${action} on ${resource}`
      );
    }
  }

  /**
   * Gets all permissions for a user
   */
  async getUserPermissions(userId: string): Promise<Permission[]> {
    const user = await this.userRepository.findOne({
      where: { id: userId },
      relations: ['roles', 'roles.permissions']
    });

    if (!user) {
      throw new NotFoundError(`User not found: ${userId}`);
    }

    return user.roles.flatMap(role => role.permissions);
  }

  /**
   * Creates a new permission
   */
  async createPermission(
    roleId: string,
    permission: Partial<Permission>
  ): Promise<Permission> {
    const role = await this.roleRepository.findOne({
      where: { id: roleId }
    });

    if (!role) {
      throw new NotFoundError(`Role not found: ${roleId}`);
    }

    const newPermission = this.permissionRepository.create({
      ...permission,
      role
    });

    const savedPermission = await this.permissionRepository.save(newPermission);

    // Invalidate relevant cache entries
    await this.invalidatePermissionCache(roleId);

    return savedPermission;
  }

  /**
   * Updates an existing permission
   */
  async updatePermission(
    id: string,
    updates: Partial<Permission>
  ): Promise<Permission> {
    const permission = await this.permissionRepository.findOne({
      where: { id },
      relations: ['role']
    });

    if (!permission) {
      throw new NotFoundError(`Permission not found: ${id}`);
    }

    Object.assign(permission, updates);
    const updatedPermission = await this.permissionRepository.save(permission);

    // Invalidate relevant cache entries
    await this.invalidatePermissionCache(permission.role.id);

    return updatedPermission;
  }

  /**
   * Deletes a permission
   */
  async deletePermission(id: string): Promise<void> {
    const permission = await this.permissionRepository.findOne({
      where: { id },
      relations: ['role']
    });

    if (!permission) {
      throw new NotFoundError(`Permission not found: ${id}`);
    }

    await this.permissionRepository.remove(permission);

    // Invalidate relevant cache entries
    await this.invalidatePermissionCache(permission.role.id);
  }

  private getCacheKey(
    userId: string,
    action: PermissionAction,
    resource: string
  ): string {
    return `${this.CACHE_PREFIX}${userId}:${action}:${resource}`;
  }

  private async invalidatePermissionCache(roleId: string): Promise<void> {
    const users = await this.userRepository.find({
      where: { roles: { id: roleId } }
    });

    // Delete all cached permissions for affected users
    await Promise.all(
      users.map(user =>
        this.cacheService.deletePattern(`${this.CACHE_PREFIX}${user.id}:*`)
      )
    );
  }
}
