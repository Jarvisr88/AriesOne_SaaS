import { Injectable } from '@nestjs/common';
import { Report } from '../entities/report.entity';
import { PDFDocument } from 'pdf-lib';
import ExcelJS from 'exceljs';
import { createReadStream } from 'fs';
import { CacheService } from './cache.service';

@Injectable()
export class ExportService {
  constructor(private cacheService: CacheService) {}

  async exportReport(report: Report, format: string, userId: string): Promise<Buffer> {
    const cacheKey = `export:${report.id}:${format}:${report.version}`;
    const cached = await this.cacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    let buffer: Buffer;
    switch (format.toLowerCase()) {
      case 'pdf':
        buffer = await this.exportToPdf(report);
        break;
      case 'excel':
        buffer = await this.exportToExcel(report);
        break;
      case 'csv':
        buffer = await this.exportToCsv(report);
        break;
      default:
        throw new Error('Unsupported export format');
    }

    // Cache the exported file for 5 minutes
    await this.cacheService.set(cacheKey, buffer, 300);

    // Log export activity
    await this.logExportActivity(report, format, userId);

    return buffer;
  }

  private async exportToPdf(report: Report): Promise<Buffer> {
    try {
      const pdfDoc = await PDFDocument.create();
      const page = pdfDoc.addPage([595.276, 841.890]); // A4 size

      // Apply template settings
      const { margins, orientation } = report.template.templateData;
      if (orientation === 'landscape') {
        page.setRotation(90);
      }

      // Add content based on template
      const { font } = await pdfDoc.embedFont('Helvetica');
      page.drawText(report.name, {
        x: margins.left,
        y: page.getHeight() - margins.top,
        font,
        size: 14,
      });

      // Add report content
      // ... implement based on template structure

      return Buffer.from(await pdfDoc.save());
    } catch (error) {
      throw new Error(`PDF export failed: ${error.message}`);
    }
  }

  private async exportToExcel(report: Report): Promise<Buffer> {
    try {
      const workbook = new ExcelJS.Workbook();
      workbook.creator = 'DMEWorks';
      workbook.lastModifiedBy = 'DMEWorks';
      workbook.created = new Date();
      workbook.modified = new Date();

      // Apply template
      const { sheets, headerStyle, dataStyle } = report.template.templateData;
      
      for (const sheetConfig of sheets) {
        const worksheet = workbook.addWorksheet(sheetConfig.name);

        // Configure sheet
        if (sheetConfig.freezePanes) {
          worksheet.views = [{ state: 'frozen', xSplit: 0, ySplit: 1 }];
        }

        // Add headers with style
        if (headerStyle) {
          worksheet.getRow(1).font = headerStyle.font;
          worksheet.getRow(1).fill = headerStyle.fill;
        }

        // Add data with style
        if (dataStyle) {
          // ... implement based on template structure
        }
      }

      return workbook.xlsx.writeBuffer() as Promise<Buffer>;
    } catch (error) {
      throw new Error(`Excel export failed: ${error.message}`);
    }
  }

  private async exportToCsv(report: Report): Promise<Buffer> {
    try {
      // Implement CSV export
      const rows: string[] = [];
      
      // Add headers
      const headers = ['Column1', 'Column2']; // Get from template
      rows.push(headers.join(','));

      // Add data rows
      // ... implement based on template structure

      return Buffer.from(rows.join('\n'));
    } catch (error) {
      throw new Error(`CSV export failed: ${error.message}`);
    }
  }

  private async logExportActivity(
    report: Report,
    format: string,
    userId: string,
  ): Promise<void> {
    await this.reportRepository.query(
      'INSERT INTO report_audit (report_id, action, changes, performed_by) VALUES ($1, $2, $3, $4)',
      [
        report.id,
        'EXPORT',
        JSON.stringify({ format, timestamp: new Date() }),
        userId,
      ],
    );
  }
}
