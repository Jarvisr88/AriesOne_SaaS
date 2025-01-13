import { injectable, inject } from 'inversify';
import { sign, verify } from 'jsonwebtoken';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';
import { CacheService } from '../cache/cache.service';
import { AuthenticationError } from '../errors';
import { User, AuthToken, TokenPayload } from '../types';

@injectable()
export class AuthService {
  private readonly jwtSecret: string;
  private readonly tokenExpiration: string;

  constructor(
    @inject(ConfigService) private readonly config: ConfigService,
    @inject(LoggerService) private readonly logger: LoggerService,
    @inject(CacheService) private readonly cache: CacheService
  ) {
    this.jwtSecret = this.config.get('auth.jwtSecret');
    this.tokenExpiration = this.config.get('auth.tokenExpiration', '1h');
  }

  async generateToken(user: User): Promise<AuthToken> {
    try {
      const payload: TokenPayload = {
        sub: user.id,
        email: user.email,
        roles: user.roles,
        iat: Math.floor(Date.now() / 1000)
      };

      const token = sign(payload, this.jwtSecret, {
        expiresIn: this.tokenExpiration
      });

      const authToken: AuthToken = {
        token,
        expiresIn: this.tokenExpiration,
        tokenType: 'Bearer'
      };

      await this.cache.set(
        `auth:token:${user.id}`,
        authToken,
        this.config.get('auth.cacheTTL', 3600)
      );

      return authToken;
    } catch (error) {
      this.logger.error('Token generation failed', { error, userId: user.id });
      throw new AuthenticationError('Failed to generate token');
    }
  }

  async validateToken(token: string): Promise<TokenPayload> {
    try {
      const payload = verify(token, this.jwtSecret) as TokenPayload;
      
      const cachedToken = await this.cache.get<AuthToken>(
        `auth:token:${payload.sub}`
      );

      if (!cachedToken) {
        throw new AuthenticationError('Token not found in cache');
      }

      return payload;
    } catch (error) {
      this.logger.error('Token validation failed', { error });
      throw new AuthenticationError('Invalid token');
    }
  }

  async revokeToken(userId: string): Promise<void> {
    try {
      await this.cache.delete(`auth:token:${userId}`);
      this.logger.info('Token revoked', { userId });
    } catch (error) {
      this.logger.error('Token revocation failed', { error, userId });
      throw new AuthenticationError('Failed to revoke token');
    }
  }

  async refreshToken(userId: string): Promise<AuthToken> {
    try {
      const user = await this.getUserById(userId);
      return this.generateToken(user);
    } catch (error) {
      this.logger.error('Token refresh failed', { error, userId });
      throw new AuthenticationError('Failed to refresh token');
    }
  }

  private async getUserById(userId: string): Promise<User> {
    // In a real implementation, this would fetch the user from a database
    const user: User = {
      id: userId,
      email: 'user@example.com',
      roles: ['user'],
      createdAt: new Date()
    };
    return user;
  }

  async hasPermission(userId: string, permission: string): Promise<boolean> {
    try {
      const user = await this.getUserById(userId);
      return user.roles.includes(permission);
    } catch (error) {
      this.logger.error('Permission check failed', { 
        error, 
        userId, 
        permission 
      });
      return false;
    }
  }
}
