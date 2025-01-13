import { Injectable } from '@nestjs/common';
import Handlebars from 'handlebars';
import { isEqual } from 'lodash';

@Injectable()
export class TemplateParser {
  private readonly handlebars: typeof Handlebars;
  private readonly compiledTemplates: Map<string, HandlebarsTemplateDelegate>;
  private readonly templateVersions: Map<string, any>;

  constructor() {
    this.handlebars = Handlebars.create();
    this.compiledTemplates = new Map();
    this.templateVersions = new Map();
    this.registerHelpers();
  }

  private registerHelpers(): void {
    // Date formatting
    this.handlebars.registerHelper('formatDate', (date: Date, format: string) => {
      return new Intl.DateTimeFormat('en-US', {
        dateStyle: format === 'short' ? 'short' : 'long',
        timeStyle: format === 'short' ? 'short' : 'long',
      }).format(date);
    });

    // Number formatting
    this.handlebars.registerHelper('formatNumber', (number: number, decimals: number = 2) => {
      return number.toFixed(decimals);
    });

    // Currency formatting
    this.handlebars.registerHelper('formatCurrency', (amount: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(amount);
    });

    // Conditional rendering
    this.handlebars.registerHelper('ifEquals', function(arg1, arg2, options) {
      return isEqual(arg1, arg2) ? options.fn(this) : options.inverse(this);
    });

    // Array operations
    this.handlebars.registerHelper('sum', (array: number[]) => {
      return array.reduce((a, b) => a + b, 0);
    });

    this.handlebars.registerHelper('average', (array: number[]) => {
      if (array.length === 0) return 0;
      return array.reduce((a, b) => a + b, 0) / array.length;
    });

    // Table helpers
    this.handlebars.registerHelper('tableRow', function(items, options) {
      const rows = items.map(item => options.fn(item)).join('');
      return new Handlebars.SafeString(`<tr>${rows}</tr>`);
    });

    this.handlebars.registerHelper('tableCell', function(content) {
      return new Handlebars.SafeString(`<td>${content}</td>`);
    });
  }

  compile(template: string, templateId: string, version: any): HandlebarsTemplateDelegate {
    const cachedVersion = this.templateVersions.get(templateId);
    const cachedTemplate = this.compiledTemplates.get(templateId);

    if (cachedTemplate && isEqual(cachedVersion, version)) {
      return cachedTemplate;
    }

    try {
      const compiled = this.handlebars.compile(template);
      this.compiledTemplates.set(templateId, compiled);
      this.templateVersions.set(templateId, version);
      return compiled;
    } catch (error) {
      throw new Error(`Template compilation failed: ${error.message}`);
    }
  }

  render(template: HandlebarsTemplateDelegate, data: any): string {
    try {
      return template(data);
    } catch (error) {
      throw new Error(`Template rendering failed: ${error.message}`);
    }
  }

  validate(template: string): boolean {
    try {
      this.handlebars.compile(template);
      return true;
    } catch (error) {
      throw new Error(`Template validation failed: ${error.message}`);
    }
  }

  parseVariables(template: string): string[] {
    const ast = this.handlebars.parse(template);
    const variables = new Set<string>();

    function traverse(node: any) {
      if (node.type === 'MustacheStatement' || node.type === 'SubExpression') {
        if (node.path.type === 'PathExpression') {
          variables.add(node.path.original);
        }
      }
      if (node.program) {
        traverse(node.program);
      }
      if (node.inverse) {
        traverse(node.inverse);
      }
      if (node.params) {
        node.params.forEach(traverse);
      }
      if (node.hash && node.hash.pairs) {
        node.hash.pairs.forEach((pair: any) => traverse(pair.value));
      }
      if (node.body) {
        node.body.forEach(traverse);
      }
    }

    traverse(ast);
    return Array.from(variables);
  }
}
