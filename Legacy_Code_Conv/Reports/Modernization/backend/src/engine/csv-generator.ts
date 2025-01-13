import { Injectable } from '@nestjs/common';
import { Parser } from 'json2csv';
import { TemplateParser } from './template-parser';

interface CsvOptions {
  delimiter?: string;
  quote?: string;
  headers?: string[];
  includeHeaders?: boolean;
  transforms?: Array<(value: any) => any>;
}

@Injectable()
export class CsvGenerator {
  constructor(private templateParser: TemplateParser) {}

  async generate(
    template: string,
    data: any,
    options: CsvOptions = {},
  ): Promise<Buffer> {
    try {
      // Parse template
      const compiledTemplate = this.templateParser.compile(template, 'csv', data);
      const content = JSON.parse(this.templateParser.render(compiledTemplate, data));

      // Configure parser options
      const parserOptions = {
        delimiter: options.delimiter || ',',
        quote: options.quote || '"',
        header: options.includeHeaders !== false,
        transforms: options.transforms || [],
      };

      // If headers are specified, use them
      if (options.headers) {
        parserOptions['fields'] = options.headers.map(header => ({
          label: header,
          value: (row: any) => this.getNestedValue(row, header),
        }));
      }

      // Create parser
      const parser = new Parser(parserOptions);

      // Convert to CSV
      const csv = parser.parse(Array.isArray(content) ? content : [content]);

      return Buffer.from(csv);
    } catch (error) {
      throw new Error(`CSV generation failed: ${error.message}`);
    }
  }

  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : null;
    }, obj);
  }

  async generateMultiSheet(
    template: string,
    data: any,
    options: CsvOptions = {},
  ): Promise<Map<string, Buffer>> {
    try {
      // Parse template
      const compiledTemplate = this.templateParser.compile(template, 'csv', data);
      const content = JSON.parse(this.templateParser.render(compiledTemplate, data));

      const results = new Map<string, Buffer>();

      // Generate CSV for each sheet
      for (const [sheetName, sheetData] of Object.entries(content)) {
        const sheetOptions = {
          ...options,
          headers: options.headers || this.extractHeaders(sheetData as any[]),
        };

        const csv = await this.generate(
          JSON.stringify(sheetData),
          null,
          sheetOptions,
        );

        results.set(sheetName, csv);
      }

      return results;
    } catch (error) {
      throw new Error(`Multi-sheet CSV generation failed: ${error.message}`);
    }
  }

  private extractHeaders(data: any[]): string[] {
    if (!Array.isArray(data) || data.length === 0) {
      return [];
    }

    const headers = new Set<string>();
    const processObject = (obj: any, prefix = '') => {
      for (const [key, value] of Object.entries(obj)) {
        const fullPath = prefix ? `${prefix}.${key}` : key;
        if (value && typeof value === 'object' && !Array.isArray(value)) {
          processObject(value, fullPath);
        } else {
          headers.add(fullPath);
        }
      }
    };

    data.forEach(item => processObject(item));
    return Array.from(headers);
  }

  async appendToFile(
    existingCsv: Buffer,
    newData: any[],
    options: CsvOptions = {},
  ): Promise<Buffer> {
    try {
      // Parse existing CSV to get headers
      const existing = existingCsv.toString('utf-8');
      const headers = existing.split('\n')[0].split(options.delimiter || ',');

      // Generate CSV for new data with matching headers
      const newCsv = await this.generate(
        JSON.stringify(newData),
        null,
        {
          ...options,
          headers,
          includeHeaders: false,
        },
      );

      // Combine existing and new CSV
      return Buffer.concat([
        existingCsv,
        Buffer.from('\n'),
        newCsv,
      ]);
    } catch (error) {
      throw new Error(`CSV append failed: ${error.message}`);
    }
  }
}
