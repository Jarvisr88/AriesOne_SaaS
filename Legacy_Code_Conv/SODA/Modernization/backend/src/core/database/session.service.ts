import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Session } from '../../domain/entities/session.entity';
import { User } from '../../domain/entities/user.entity';
import { CacheService } from '../cache/cache.service';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';
import { EventEmitter2 } from '@nestjs/event-emitter';
import { SessionExpiredError, UnauthorizedError } from '../errors';

export interface SessionData {
  userId: string;
  ip: string;
  userAgent: string;
  metadata?: Record<string, any>;
}

@Injectable()
export class SessionService implements OnModuleInit, OnModuleDestroy {
  private readonly SESSION_TTL = 3600; // 1 hour
  private readonly CLEANUP_INTERVAL = 300000; // 5 minutes
  private cleanupInterval: NodeJS.Timeout;

  constructor(
    @InjectRepository(Session)
    private readonly sessionRepository: Repository<Session>,
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
    private readonly cache: CacheService,
    private readonly config: ConfigService,
    private readonly logger: LoggerService,
    private readonly eventEmitter: EventEmitter2
  ) {}

  async onModuleInit() {
    // Start cleanup interval
    this.cleanupInterval = setInterval(
      () => this.cleanupExpiredSessions(),
      this.CLEANUP_INTERVAL
    );
  }

  async onModuleDestroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
  }

  /**
   * Creates a new session
   */
  async createSession(data: SessionData): Promise<Session> {
    const user = await this.userRepository.findOne({
      where: { id: data.userId }
    });

    if (!user) {
      throw new UnauthorizedError('User not found');
    }

    const session = this.sessionRepository.create({
      user,
      ip: data.ip,
      userAgent: data.userAgent,
      metadata: data.metadata,
      lastActivity: new Date(),
      expiresAt: new Date(Date.now() + this.SESSION_TTL * 1000)
    });

    const savedSession = await this.sessionRepository.save(session);

    // Cache session
    await this.cache.set(
      this.getSessionCacheKey(savedSession.id),
      savedSession,
      this.SESSION_TTL
    );

    // Emit event
    this.eventEmitter.emit('session.created', savedSession);

    return savedSession;
  }

  /**
   * Gets a session by ID
   */
  async getSession(id: string): Promise<Session> {
    // Try cache first
    const cached = await this.cache.get<Session>(
      this.getSessionCacheKey(id)
    );
    if (cached) {
      return cached;
    }

    // Get from database
    const session = await this.sessionRepository.findOne({
      where: { id },
      relations: ['user']
    });

    if (!session) {
      throw new UnauthorizedError('Session not found');
    }

    if (session.isExpired()) {
      await this.destroySession(id);
      throw new SessionExpiredError();
    }

    // Cache for future use
    await this.cache.set(
      this.getSessionCacheKey(id),
      session,
      this.SESSION_TTL
    );

    return session;
  }

  /**
   * Updates session activity
   */
  async updateSession(id: string): Promise<void> {
    const session = await this.getSession(id);
    
    session.lastActivity = new Date();
    session.expiresAt = new Date(Date.now() + this.SESSION_TTL * 1000);
    
    await this.sessionRepository.save(session);

    // Update cache
    await this.cache.set(
      this.getSessionCacheKey(id),
      session,
      this.SESSION_TTL
    );
  }

  /**
   * Destroys a session
   */
  async destroySession(id: string): Promise<void> {
    const session = await this.sessionRepository.findOne({
      where: { id }
    });

    if (session) {
      await this.sessionRepository.remove(session);
      await this.cache.delete(this.getSessionCacheKey(id));
      
      // Emit event
      this.eventEmitter.emit('session.destroyed', { sessionId: id });
    }
  }

  /**
   * Gets all active sessions for a user
   */
  async getUserSessions(userId: string): Promise<Session[]> {
    return this.sessionRepository.find({
      where: {
        user: { id: userId },
        expiresAt: { $gt: new Date() }
      },
      order: { lastActivity: 'DESC' }
    });
  }

  /**
   * Destroys all sessions for a user
   */
  async destroyUserSessions(userId: string): Promise<void> {
    const sessions = await this.getUserSessions(userId);
    
    await Promise.all(
      sessions.map(session => this.destroySession(session.id))
    );
  }

  /**
   * Cleans up expired sessions
   */
  private async cleanupExpiredSessions(): Promise<void> {
    try {
      const expiredSessions = await this.sessionRepository.find({
        where: {
          expiresAt: { $lt: new Date() }
        }
      });

      await Promise.all(
        expiredSessions.map(session => this.destroySession(session.id))
      );

      this.logger.debug(
        `Cleaned up ${expiredSessions.length} expired sessions`
      );
    } catch (error) {
      this.logger.error('Error cleaning up expired sessions', { error });
    }
  }

  private getSessionCacheKey(sessionId: string): string {
    return `session:${sessionId}`;
  }
}
