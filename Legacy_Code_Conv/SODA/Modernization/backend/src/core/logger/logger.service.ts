import { injectable, inject } from 'inversify';
import { createLogger, format, transports, Logger } from 'winston';
import { ConfigService } from '../config/config.service';

@injectable()
export class LoggerService {
  private readonly logger: Logger;

  constructor(
    @inject(ConfigService) private readonly config: ConfigService
  ) {
    const logLevel = this.config.get('logger.level', 'info');
    const environment = this.config.get('app.environment', 'development');

    this.logger = createLogger({
      level: logLevel,
      format: format.combine(
        format.timestamp(),
        format.errors({ stack: true }),
        format.metadata(),
        environment === 'development' 
          ? format.prettyPrint() 
          : format.json()
      ),
      defaultMeta: {
        service: 'soda-service',
        environment
      },
      transports: this.createTransports()
    });
  }

  private createTransports() {
    const transportsArray = [
      new transports.Console({
        format: format.combine(
          format.colorize(),
          format.simple()
        )
      })
    ];

    const logFile = this.config.get('logger.file');
    if (logFile) {
      transportsArray.push(
        new transports.File({
          filename: logFile,
          maxsize: 5242880, // 5MB
          maxFiles: 5,
          format: format.json()
        })
      );
    }

    return transportsArray;
  }

  debug(message: string, meta?: any): void {
    this.logger.debug(message, meta);
  }

  info(message: string, meta?: any): void {
    this.logger.info(message, meta);
  }

  warn(message: string, meta?: any): void {
    this.logger.warn(message, meta);
  }

  error(message: string, meta?: any): void {
    this.logger.error(message, meta);
  }

  fatal(message: string, meta?: any): void {
    this.logger.error(message, { ...meta, level: 'fatal' });
  }

  startRequest(requestId: string, method: string, url: string): void {
    this.info('Request started', {
      requestId,
      method,
      url,
      timestamp: new Date().toISOString()
    });
  }

  endRequest(requestId: string, statusCode: number, duration: number): void {
    this.info('Request completed', {
      requestId,
      statusCode,
      duration,
      timestamp: new Date().toISOString()
    });
  }

  logError(error: Error, requestId?: string): void {
    this.error('Error occurred', {
      requestId,
      error: {
        message: error.message,
        stack: error.stack,
        name: error.name
      },
      timestamp: new Date().toISOString()
    });
  }

  logMetric(name: string, value: number, tags?: Record<string, string>): void {
    this.info('Metric recorded', {
      metric: name,
      value,
      tags,
      timestamp: new Date().toISOString()
    });
  }
}
