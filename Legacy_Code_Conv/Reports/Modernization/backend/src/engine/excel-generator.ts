import { Injectable } from '@nestjs/common';
import ExcelJS from 'exceljs';
import { TemplateParser } from './template-parser';

interface ExcelOptions {
  sheets: Array<{
    name: string;
    freezePanes?: [number, number];
    columns?: Array<{
      header: string;
      key: string;
      width?: number;
      style?: any;
    }>;
  }>;
  headerStyle?: {
    font?: any;
    fill?: any;
    border?: any;
  };
  dataStyle?: {
    font?: any;
    fill?: any;
    border?: any;
  };
}

@Injectable()
export class ExcelGenerator {
  constructor(private templateParser: TemplateParser) {}

  async generate(
    template: string,
    data: any,
    options: ExcelOptions,
  ): Promise<Buffer> {
    try {
      // Create workbook
      const workbook = new ExcelJS.Workbook();
      workbook.creator = data.author || 'DMEWorks';
      workbook.lastModifiedBy = data.author || 'DMEWorks';
      workbook.created = new Date();
      workbook.modified = new Date();

      // Parse template
      const compiledTemplate = this.templateParser.compile(template, 'excel', data);
      const content = JSON.parse(this.templateParser.render(compiledTemplate, data));

      // Process each sheet
      for (const sheetConfig of options.sheets) {
        const worksheet = workbook.addWorksheet(sheetConfig.name);

        // Set freeze panes if specified
        if (sheetConfig.freezePanes) {
          worksheet.views = [{
            state: 'frozen',
            xSplit: sheetConfig.freezePanes[1],
            ySplit: sheetConfig.freezePanes[0],
          }];
        }

        // Set columns if specified
        if (sheetConfig.columns) {
          worksheet.columns = sheetConfig.columns.map(col => ({
            header: col.header,
            key: col.key,
            width: col.width || 15,
            style: this.mergeStyles(options.headerStyle, col.style),
          }));
        }

        // Add data
        const sheetData = content[sheetConfig.name];
        if (Array.isArray(sheetData)) {
          // Add rows with data style
          worksheet.addRows(sheetData);
          if (options.dataStyle) {
            const dataRows = worksheet.getRows(2, sheetData.length) || [];
            for (const row of dataRows) {
              row.eachCell(cell => {
                Object.assign(cell, options.dataStyle);
              });
            }
          }
        }

        // Apply conditional formatting
        await this.applyConditionalFormatting(worksheet, sheetConfig);

        // Auto-filter if columns are present
        if (sheetConfig.columns) {
          worksheet.autoFilter = {
            from: { row: 1, column: 1 },
            to: { row: 1, column: sheetConfig.columns.length },
          };
        }
      }

      // Generate buffer
      return workbook.xlsx.writeBuffer() as Promise<Buffer>;
    } catch (error) {
      throw new Error(`Excel generation failed: ${error.message}`);
    }
  }

  private mergeStyles(...styles: any[]): any {
    return styles.reduce((merged, style) => {
      if (!style) return merged;
      return {
        ...merged,
        font: { ...merged.font, ...style.font },
        fill: { ...merged.fill, ...style.fill },
        border: { ...merged.border, ...style.border },
      };
    }, {});
  }

  private async applyConditionalFormatting(
    worksheet: ExcelJS.Worksheet,
    sheetConfig: any,
  ): Promise<void> {
    if (!sheetConfig.conditionalFormatting) return;

    for (const rule of sheetConfig.conditionalFormatting) {
      const { range, type, criteria, style } = rule;

      switch (type) {
        case 'cellIs':
          worksheet.addConditionalFormatting({
            ref: range,
            rules: [{
              type: 'cellIs',
              operator: criteria.operator,
              formulae: [criteria.value],
              style: style,
            }],
          });
          break;

        case 'containsText':
          worksheet.addConditionalFormatting({
            ref: range,
            rules: [{
              type: 'containsText',
              operator: 'containsText',
              text: criteria.text,
              style: style,
            }],
          });
          break;

        case 'colorScale':
          worksheet.addConditionalFormatting({
            ref: range,
            rules: [{
              type: 'colorScale',
              cfvo: criteria.points,
              color: criteria.colors,
            }],
          });
          break;

        case 'dataBar':
          worksheet.addConditionalFormatting({
            ref: range,
            rules: [{
              type: 'dataBar',
              cfvo: criteria.points,
              color: criteria.color,
            }],
          });
          break;
      }
    }
  }
}
