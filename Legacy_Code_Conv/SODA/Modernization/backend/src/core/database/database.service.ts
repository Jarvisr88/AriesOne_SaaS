import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { InjectEntityManager, InjectConnection } from '@nestjs/typeorm';
import { EntityManager, Connection, QueryRunner } from 'typeorm';
import { Subject, Observable } from 'rxjs';
import { filter } from 'rxjs/operators';
import { LoggerService } from '../logger/logger.service';
import { MetricsService } from '../metrics/metrics.service';
import { ConfigService } from '../config/config.service';
import { DatabaseError } from '../errors';

export interface DatabaseEvent {
  type: 'change' | 'error';
  table?: string;
  error?: Error;
  timestamp: Date;
}

@Injectable()
export class DatabaseService implements OnModuleInit, OnModuleDestroy {
  private readonly events = new Subject<DatabaseEvent>();
  private queryRunner: QueryRunner;
  private notificationListener: any;
  private readonly RETRY_ATTEMPTS = 3;
  private readonly RETRY_DELAY = 1000; // 1 second

  constructor(
    @InjectEntityManager()
    private readonly entityManager: EntityManager,
    @InjectConnection()
    private readonly connection: Connection,
    private readonly logger: LoggerService,
    private readonly metrics: MetricsService,
    private readonly config: ConfigService
  ) {}

  async onModuleInit() {
    await this.setupNotifications();
  }

  async onModuleDestroy() {
    await this.cleanupNotifications();
  }

  /**
   * Executes a query with automatic retries and metrics
   */
  async executeQuery<T>(
    query: string,
    parameters: any[] = [],
    options: {
      retryAttempts?: number;
      timeout?: number;
    } = {}
  ): Promise<T> {
    const startTime = Date.now();
    const retryAttempts = options.retryAttempts ?? this.RETRY_ATTEMPTS;
    let lastError: Error;

    for (let attempt = 1; attempt <= retryAttempts; attempt++) {
      try {
        const result = await this.entityManager.query(query, parameters);
        
        // Record metrics
        this.metrics.recordDbQuery({
          query,
          duration: Date.now() - startTime,
          success: true
        });

        return result;
      } catch (error) {
        lastError = error;
        this.logger.warn(`Query attempt ${attempt} failed`, {
          query,
          error,
          attempt
        });

        // Record failed attempt
        this.metrics.recordDbQuery({
          query,
          duration: Date.now() - startTime,
          success: false,
          error
        });

        if (attempt < retryAttempts) {
          await new Promise(resolve => 
            setTimeout(resolve, this.RETRY_DELAY * attempt)
          );
        }
      }
    }

    throw new DatabaseError(
      `Query failed after ${retryAttempts} attempts`,
      lastError
    );
  }

  /**
   * Executes a query within a transaction
   */
  async executeTransaction<T>(
    callback: (entityManager: EntityManager) => Promise<T>
  ): Promise<T> {
    const queryRunner = this.connection.createQueryRunner();
    await queryRunner.connect();
    await queryRunner.startTransaction();

    try {
      const result = await callback(queryRunner.manager);
      await queryRunner.commitTransaction();
      return result;
    } catch (error) {
      await queryRunner.rollbackTransaction();
      throw error;
    } finally {
      await queryRunner.release();
    }
  }

  /**
   * Subscribes to database changes for specific tables
   */
  onDatabaseChange(tables?: string[]): Observable<DatabaseEvent> {
    return this.events.pipe(
      filter(event => 
        event.type === 'change' &&
        (!tables || !event.table || tables.includes(event.table))
      )
    );
  }

  /**
   * Gets the current database status
   */
  async getStatus(): Promise<{
    connected: boolean;
    poolSize: number;
    activeConnections: number;
    idleConnections: number;
    waitingConnections: number;
  }> {
    const pool = (this.connection.driver as any).pool;
    
    return {
      connected: this.connection.isConnected,
      poolSize: pool.totalCount,
      activeConnections: pool.activeCount,
      idleConnections: pool.idleCount,
      waitingConnections: pool.waitingCount
    };
  }

  /**
   * Checks database connectivity
   */
  async checkConnection(): Promise<boolean> {
    try {
      await this.connection.query('SELECT 1');
      return true;
    } catch (error) {
      this.logger.error('Database connection check failed', { error });
      return false;
    }
  }

  private async setupNotifications() {
    this.queryRunner = this.connection.createQueryRunner();
    await this.queryRunner.connect();

    // Listen for database notifications
    this.notificationListener = (channel: string, payload: string) => {
      try {
        const data = JSON.parse(payload);
        this.events.next({
          type: 'change',
          table: data.table,
          timestamp: new Date()
        });
      } catch (error) {
        this.logger.error('Error processing database notification', { error });
        this.events.next({
          type: 'error',
          error,
          timestamp: new Date()
        });
      }
    };

    await this.queryRunner.query(`
      CREATE OR REPLACE FUNCTION notify_table_change()
      RETURNS trigger AS $$
      BEGIN
        PERFORM pg_notify(
          'table_change',
          json_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'schema', TG_TABLE_SCHEMA
          )::text
        );
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;
    `);

    // Subscribe to notifications
    await this.queryRunner.query('LISTEN table_change');
    (this.connection.driver as any).postgres.on(
      'notification',
      this.notificationListener
    );
  }

  private async cleanupNotifications() {
    if (this.notificationListener) {
      (this.connection.driver as any).postgres.removeListener(
        'notification',
        this.notificationListener
      );
    }

    if (this.queryRunner) {
      await this.queryRunner.query('UNLISTEN table_change');
      await this.queryRunner.release();
    }
  }
}
