import { injectable } from 'inversify';
import { ValidationError } from '../errors';

@injectable()
export class JsonUtil {
  private readonly MAX_DEPTH = 100;
  private readonly CIRCULAR_PLACEHOLDER = '[Circular Reference]';

  serialize(value: any, options: SerializeOptions = {}): string {
    const {
      pretty = false,
      escapeHTML = false,
      maxDepth = this.MAX_DEPTH
    } = options;

    try {
      const seen = new WeakSet();
      const serialized = JSON.stringify(
        value,
        (key, value) => {
          if (typeof value === 'object' && value !== null) {
            if (seen.has(value)) {
              return this.CIRCULAR_PLACEHOLDER;
            }
            seen.add(value);
          }
          return this.transformValue(value, escapeHTML);
        },
        pretty ? 2 : undefined
      );

      return serialized;
    } catch (error) {
      throw new ValidationError(`JSON serialization failed: ${error.message}`);
    }
  }

  deserialize<T = any>(value: string, options: DeserializeOptions = {}): T {
    const { reviver } = options;

    try {
      return JSON.parse(value, reviver);
    } catch (error) {
      throw new ValidationError(`JSON deserialization failed: ${error.message}`);
    }
  }

  private transformValue(value: any, escapeHTML: boolean): any {
    if (typeof value === 'string' && escapeHTML) {
      return this.escapeHTML(value);
    }

    if (value instanceof Date) {
      return value.toISOString();
    }

    if (value instanceof RegExp) {
      return value.toString();
    }

    if (typeof value === 'bigint') {
      return value.toString();
    }

    if (value instanceof Set) {
      return Array.from(value);
    }

    if (value instanceof Map) {
      return Object.fromEntries(value);
    }

    if (ArrayBuffer.isView(value)) {
      return Array.from(value as any);
    }

    return value;
  }

  private escapeHTML(str: string): string {
    const htmlEscapes: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    };

    return str.replace(/[&<>"']/g, char => htmlEscapes[char]);
  }

  merge(target: any, source: any, options: MergeOptions = {}): any {
    const {
      deep = true,
      arrayMerge = 'replace',
      skipNull = false,
      skipUndefined = false
    } = options;

    if (!source || typeof source !== 'object') {
      return target;
    }

    const result = Array.isArray(target) ? [...target] : { ...target };

    for (const key in source) {
      if (Object.prototype.hasOwnProperty.call(source, key)) {
        const sourceValue = source[key];

        if (skipNull && sourceValue === null) continue;
        if (skipUndefined && sourceValue === undefined) continue;

        if (deep && sourceValue && typeof sourceValue === 'object') {
          const targetValue = result[key];

          if (Array.isArray(sourceValue)) {
            result[key] = this.mergeArrays(
              Array.isArray(targetValue) ? targetValue : [],
              sourceValue,
              arrayMerge
            );
          } else {
            result[key] = this.merge(
              targetValue || {},
              sourceValue,
              options
            );
          }
        } else {
          result[key] = sourceValue;
        }
      }
    }

    return result;
  }

  private mergeArrays(
    target: any[],
    source: any[],
    strategy: ArrayMergeStrategy
  ): any[] {
    switch (strategy) {
      case 'replace':
        return [...source];
      case 'concat':
        return [...target, ...source];
      case 'unique':
        return Array.from(new Set([...target, ...source]));
      default:
        return [...source];
    }
  }

  diff(obj1: any, obj2: any, options: DiffOptions = {}): any {
    const {
      deep = true,
      includeUnchanged = false,
      arrayComparison = 'strict'
    } = options;

    if (obj1 === obj2) {
      return includeUnchanged ? obj1 : undefined;
    }

    if (!obj1 || !obj2 || typeof obj1 !== 'object' || typeof obj2 !== 'object') {
      return obj2;
    }

    if (Array.isArray(obj1) && Array.isArray(obj2)) {
      return this.diffArrays(obj1, obj2, arrayComparison);
    }

    const diff: any = {};
    const allKeys = new Set([...Object.keys(obj1), ...Object.keys(obj2)]);

    for (const key of allKeys) {
      const value1 = obj1[key];
      const value2 = obj2[key];

      if (deep && value1 && value2 && typeof value1 === 'object' && typeof value2 === 'object') {
        const nestedDiff = this.diff(value1, value2, options);
        if (nestedDiff !== undefined) {
          diff[key] = nestedDiff;
        }
      } else if (value1 !== value2 || includeUnchanged) {
        diff[key] = value2;
      }
    }

    return Object.keys(diff).length > 0 ? diff : undefined;
  }

  private diffArrays(arr1: any[], arr2: any[], comparison: ArrayComparisonStrategy): any[] | undefined {
    switch (comparison) {
      case 'strict':
        return JSON.stringify(arr1) === JSON.stringify(arr2) ? undefined : arr2;
      case 'length':
        return arr1.length === arr2.length ? undefined : arr2;
      case 'subset':
        return arr2.every(item => arr1.includes(item)) ? undefined : arr2;
      default:
        return arr2;
    }
  }

  validate(value: string): boolean {
    try {
      JSON.parse(value);
      return true;
    } catch {
      return false;
    }
  }

  getValueByPath(obj: any, path: string): any {
    return path.split('.').reduce((acc, part) => {
      if (acc === null || acc === undefined) {
        return acc;
      }
      return acc[part];
    }, obj);
  }

  setValueByPath(obj: any, path: string, value: any): any {
    const parts = path.split('.');
    const lastPart = parts.pop()!;
    const target = parts.reduce((acc, part) => {
      if (!(part in acc)) {
        acc[part] = {};
      }
      return acc[part];
    }, obj);

    target[lastPart] = value;
    return obj;
  }
}

interface SerializeOptions {
  pretty?: boolean;
  escapeHTML?: boolean;
  maxDepth?: number;
}

interface DeserializeOptions {
  reviver?: (key: string, value: any) => any;
}

interface MergeOptions {
  deep?: boolean;
  arrayMerge?: ArrayMergeStrategy;
  skipNull?: boolean;
  skipUndefined?: boolean;
}

type ArrayMergeStrategy = 'replace' | 'concat' | 'unique';

interface DiffOptions {
  deep?: boolean;
  includeUnchanged?: boolean;
  arrayComparison?: ArrayComparisonStrategy;
}

type ArrayComparisonStrategy = 'strict' | 'length' | 'subset';
