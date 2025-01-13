import { injectable } from 'inversify';
import { ValidationError } from '../errors';

@injectable()
export class UriUtil {
  private readonly URL_REGEX = /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\u00a1-\uffff][a-z0-9\u00a1-\uffff_-]{0,62})?[a-z0-9\u00a1-\uffff]\.)+(?:[a-z\u00a1-\uffff]{2,}\.?))(?::\d{2,5})?(?:[/?#]\S*)?$/i;

  buildUrl(base: string, path?: string, params?: Record<string, any>): string {
    try {
      const url = new URL(path || '', base);

      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
              value.forEach(v => url.searchParams.append(key, v.toString()));
            } else {
              url.searchParams.set(key, value.toString());
            }
          }
        });
      }

      return url.toString();
    } catch (error) {
      throw new ValidationError(`Invalid URL: ${error.message}`);
    }
  }

  parseUrl(url: string): URLParts {
    try {
      const parsed = new URL(url);
      return {
        protocol: parsed.protocol.replace(':', ''),
        hostname: parsed.hostname,
        port: parsed.port ? parseInt(parsed.port, 10) : undefined,
        path: parsed.pathname,
        query: Object.fromEntries(parsed.searchParams),
        fragment: parsed.hash.replace('#', '') || undefined,
        username: parsed.username || undefined,
        password: parsed.password || undefined
      };
    } catch (error) {
      throw new ValidationError(`Invalid URL: ${error.message}`);
    }
  }

  isValidUrl(url: string): boolean {
    return this.URL_REGEX.test(url);
  }

  joinPaths(...parts: string[]): string {
    return parts
      .map(part => part.trim().replace(/^\/+|\/+$/g, ''))
      .filter(Boolean)
      .join('/');
  }

  encodeQueryParams(params: Record<string, any>): string {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v.toString()));
        } else if (typeof value === 'object') {
          searchParams.set(key, JSON.stringify(value));
        } else {
          searchParams.set(key, value.toString());
        }
      }
    });

    return searchParams.toString();
  }

  decodeQueryParams(query: string): Record<string, any> {
    const params: Record<string, any> = {};
    const searchParams = new URLSearchParams(query);

    searchParams.forEach((value, key) => {
      if (params[key]) {
        if (!Array.isArray(params[key])) {
          params[key] = [params[key]];
        }
        params[key].push(this.parseQueryValue(value));
      } else {
        params[key] = this.parseQueryValue(value);
      }
    });

    return params;
  }

  private parseQueryValue(value: string): any {
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  }

  normalizeUrl(url: string, options: NormalizeOptions = {}): string {
    const {
      removeTrailingSlash = true,
      removeQueryParams = false,
      removeHash = false,
      forceHttps = false,
      stripWWW = false,
      stripAuthentication = false
    } = options;

    try {
      const parsed = new URL(url);

      if (forceHttps) {
        parsed.protocol = 'https:';
      }

      if (stripWWW && parsed.hostname.startsWith('www.')) {
        parsed.hostname = parsed.hostname.slice(4);
      }

      if (stripAuthentication) {
        parsed.username = '';
        parsed.password = '';
      }

      if (removeQueryParams) {
        parsed.search = '';
      }

      if (removeHash) {
        parsed.hash = '';
      }

      let normalized = parsed.toString();

      if (removeTrailingSlash && normalized.endsWith('/')) {
        normalized = normalized.slice(0, -1);
      }

      return normalized;
    } catch (error) {
      throw new ValidationError(`Invalid URL: ${error.message}`);
    }
  }

  resolveRelativeUrl(base: string, relative: string): string {
    try {
      return new URL(relative, base).toString();
    } catch (error) {
      throw new ValidationError(`Invalid URL: ${error.message}`);
    }
  }

  getPathSegments(url: string): string[] {
    try {
      const path = new URL(url).pathname;
      return path.split('/').filter(Boolean);
    } catch (error) {
      throw new ValidationError(`Invalid URL: ${error.message}`);
    }
  }

  sanitizeUrl(url: string): string {
    if (!url) {
      return '';
    }

    try {
      const parsed = new URL(url);
      const allowedProtocols = ['http:', 'https:', 'ftp:', 'ftps:', 'mailto:'];

      if (!allowedProtocols.includes(parsed.protocol)) {
        throw new Error('Invalid protocol');
      }

      return parsed.toString();
    } catch {
      return '';
    }
  }
}

interface URLParts {
  protocol: string;
  hostname: string;
  port?: number;
  path: string;
  query: Record<string, string>;
  fragment?: string;
  username?: string;
  password?: string;
}

interface NormalizeOptions {
  removeTrailingSlash?: boolean;
  removeQueryParams?: boolean;
  removeHash?: boolean;
  forceHttps?: boolean;
  stripWWW?: boolean;
  stripAuthentication?: boolean;
}
