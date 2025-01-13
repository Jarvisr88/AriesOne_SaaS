import { Test, TestingModule } from '@nestjs/testing';
import { TemplateParser } from '../template-parser';

describe('TemplateParser', () => {
  let parser: TemplateParser;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [TemplateParser],
    }).compile();

    parser = module.get<TemplateParser>(TemplateParser);
  });

  it('should be defined', () => {
    expect(parser).toBeDefined();
  });

  describe('compile', () => {
    it('should compile valid template', () => {
      const template = 'Hello {{name}}!';
      const compiled = parser.compile(template, 'test', { version: 1 });
      expect(compiled).toBeDefined();
      expect(typeof compiled).toBe('function');
    });

    it('should cache compiled template', () => {
      const template = 'Hello {{name}}!';
      const version = { version: 1 };
      
      const compiled1 = parser.compile(template, 'test', version);
      const compiled2 = parser.compile(template, 'test', version);
      
      expect(compiled1).toBe(compiled2);
    });

    it('should recompile on version change', () => {
      const template = 'Hello {{name}}!';
      
      const compiled1 = parser.compile(template, 'test', { version: 1 });
      const compiled2 = parser.compile(template, 'test', { version: 2 });
      
      expect(compiled1).not.toBe(compiled2);
    });

    it('should throw on invalid template', () => {
      const template = 'Hello {{name!';
      expect(() => parser.compile(template, 'test', { version: 1 })).toThrow();
    });
  });

  describe('render', () => {
    it('should render template with data', () => {
      const template = 'Hello {{name}}!';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const result = parser.render(compiled, { name: 'World' });
      expect(result).toBe('Hello World!');
    });

    it('should handle nested data', () => {
      const template = '{{user.name}} is {{user.age}} years old';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const result = parser.render(compiled, {
        user: { name: 'John', age: 30 },
      });
      expect(result).toBe('John is 30 years old');
    });

    it('should handle arrays', () => {
      const template = '{{#each items}}{{this}}{{/each}}';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const result = parser.render(compiled, { items: ['a', 'b', 'c'] });
      expect(result).toBe('abc');
    });

    it('should handle conditionals', () => {
      const template = '{{#if show}}Yes{{else}}No{{/if}}';
      const compiled = parser.compile(template, 'test', { version: 1 });
      expect(parser.render(compiled, { show: true })).toBe('Yes');
      expect(parser.render(compiled, { show: false })).toBe('No');
    });
  });

  describe('helpers', () => {
    it('should format dates', () => {
      const template = '{{formatDate date "short"}}';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const date = new Date('2025-01-01T12:00:00Z');
      const result = parser.render(compiled, { date });
      expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{2}/);
    });

    it('should format numbers', () => {
      const template = '{{formatNumber value 2}}';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const result = parser.render(compiled, { value: 123.456 });
      expect(result).toBe('123.46');
    });

    it('should format currency', () => {
      const template = '{{formatCurrency value}}';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const result = parser.render(compiled, { value: 1234.56 });
      expect(result).toBe('$1,234.56');
    });

    it('should handle array operations', () => {
      const template = '{{sum numbers}}';
      const compiled = parser.compile(template, 'test', { version: 1 });
      const result = parser.render(compiled, { numbers: [1, 2, 3] });
      expect(result).toBe('6');
    });
  });

  describe('parseVariables', () => {
    it('should extract simple variables', () => {
      const template = 'Hello {{name}}, {{greeting}}!';
      const variables = parser.parseVariables(template);
      expect(variables).toEqual(['name', 'greeting']);
    });

    it('should extract nested variables', () => {
      const template = '{{user.name}} {{user.address.city}}';
      const variables = parser.parseVariables(template);
      expect(variables).toEqual(['user.name', 'user.address.city']);
    });

    it('should extract variables from helpers', () => {
      const template = '{{formatDate date}} {{formatNumber value}}';
      const variables = parser.parseVariables(template);
      expect(variables).toContain('formatDate');
      expect(variables).toContain('formatNumber');
      expect(variables).toContain('date');
      expect(variables).toContain('value');
    });

    it('should extract variables from conditionals', () => {
      const template = '{{#if show}}{{value}}{{/if}}';
      const variables = parser.parseVariables(template);
      expect(variables).toContain('show');
      expect(variables).toContain('value');
    });
  });
});
