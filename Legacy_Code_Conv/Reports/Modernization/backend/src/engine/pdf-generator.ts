import { Injectable } from '@nestjs/common';
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import { TemplateParser } from './template-parser';

interface PdfOptions {
  format: string;
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  header?: boolean;
  footer?: boolean;
}

@Injectable()
export class PdfGenerator {
  constructor(private templateParser: TemplateParser) {}

  async generate(
    template: string,
    data: any,
    options: PdfOptions,
  ): Promise<Buffer> {
    try {
      // Create PDF document
      const pdfDoc = await PDFDocument.create();
      
      // Set metadata
      pdfDoc.setTitle(data.title || 'Report');
      pdfDoc.setAuthor(data.author || 'DMEWorks');
      pdfDoc.setCreator('DMEWorks Report Engine');
      
      // Get page dimensions
      const { width, height } = this.getPageDimensions(options.format);
      
      // Create page with proper orientation
      const page = pdfDoc.addPage([
        options.orientation === 'landscape' ? height : width,
        options.orientation === 'landscape' ? width : height,
      ]);

      // Embed font
      const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
      
      // Parse template
      const compiledTemplate = this.templateParser.compile(template, 'pdf', data);
      const content = this.templateParser.render(compiledTemplate, data);

      // Draw header if enabled
      let currentY = height - options.margins.top;
      if (options.header) {
        currentY = await this.drawHeader(page, data, {
          font: boldFont,
          margins: options.margins,
          width,
          startY: currentY,
        });
      }

      // Draw content sections
      const sections = this.parseContentSections(content);
      for (const section of sections) {
        currentY = await this.drawSection(page, section, {
          font,
          margins: options.margins,
          width,
          startY: currentY,
        });

        // Add new page if needed
        if (currentY < options.margins.bottom) {
          const newPage = pdfDoc.addPage([
            options.orientation === 'landscape' ? height : width,
            options.orientation === 'landscape' ? width : height,
          ]);
          page = newPage;
          currentY = height - options.margins.top;
        }
      }

      // Draw footer if enabled
      if (options.footer) {
        await this.drawFooter(page, data, {
          font,
          margins: options.margins,
          width,
          height,
        });
      }

      // Save document
      return Buffer.from(await pdfDoc.save());
    } catch (error) {
      throw new Error(`PDF generation failed: ${error.message}`);
    }
  }

  private getPageDimensions(format: string): { width: number; height: number } {
    const formats = {
      'A4': { width: 595.276, height: 841.890 },
      'Letter': { width: 612, height: 792 },
      'Legal': { width: 612, height: 1008 },
    };
    return formats[format] || formats['A4'];
  }

  private async drawHeader(
    page: PDFPage,
    data: any,
    options: {
      font: PDFFont;
      margins: { left: number; right: number };
      width: number;
      startY: number;
    },
  ): Promise<number> {
    const { font, margins, width, startY } = options;
    
    // Draw logo if available
    let currentX = margins.left;
    if (data.logo) {
      const logo = await this.embedImage(page, data.logo);
      page.drawImage(logo, {
        x: currentX,
        y: startY - 40,
        width: 100,
        height: 40,
      });
      currentX += 120;
    }

    // Draw title
    page.drawText(data.title || 'Report', {
      x: currentX,
      y: startY - 20,
      font,
      size: 16,
      color: rgb(0, 0, 0),
    });

    // Draw subtitle if available
    if (data.subtitle) {
      page.drawText(data.subtitle, {
        x: currentX,
        y: startY - 40,
        font,
        size: 12,
        color: rgb(0.4, 0.4, 0.4),
      });
    }

    return startY - 60;
  }

  private async drawSection(
    page: PDFPage,
    section: any,
    options: {
      font: PDFFont;
      margins: { left: number; right: number };
      width: number;
      startY: number;
    },
  ): Promise<number> {
    const { font, margins, width, startY } = options;
    let currentY = startY;

    // Draw section title
    if (section.title) {
      page.drawText(section.title, {
        x: margins.left,
        y: currentY,
        font,
        size: 14,
        color: rgb(0, 0, 0),
      });
      currentY -= 20;
    }

    // Draw section content
    const contentWidth = width - margins.left - margins.right;
    const lines = this.wrapText(section.content, font, 12, contentWidth);
    
    for (const line of lines) {
      page.drawText(line, {
        x: margins.left,
        y: currentY,
        font,
        size: 12,
        color: rgb(0, 0, 0),
      });
      currentY -= 15;
    }

    return currentY - 10;
  }

  private async drawFooter(
    page: PDFPage,
    data: any,
    options: {
      font: PDFFont;
      margins: { left: number; right: number };
      width: number;
      height: number;
    },
  ): Promise<void> {
    const { font, margins, width, height } = options;
    const footerY = margins.bottom + 20;

    // Draw page number
    const pageNumber = `Page ${page.getNodeNameNumber()}`;
    const pageNumberWidth = font.widthOfTextAtSize(pageNumber, 10);
    
    page.drawText(pageNumber, {
      x: width - margins.right - pageNumberWidth,
      y: footerY,
      font,
      size: 10,
      color: rgb(0.4, 0.4, 0.4),
    });

    // Draw timestamp
    const timestamp = new Date().toLocaleString();
    page.drawText(timestamp, {
      x: margins.left,
      y: footerY,
      font,
      size: 10,
      color: rgb(0.4, 0.4, 0.4),
    });
  }

  private wrapText(
    text: string,
    font: PDFFont,
    fontSize: number,
    maxWidth: number,
  ): string[] {
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = words[0];

    for (let i = 1; i < words.length; i++) {
      const word = words[i];
      const width = font.widthOfTextAtSize(`${currentLine} ${word}`, fontSize);
      
      if (width < maxWidth) {
        currentLine += ` ${word}`;
      } else {
        lines.push(currentLine);
        currentLine = word;
      }
    }
    
    lines.push(currentLine);
    return lines;
  }

  private async embedImage(page: PDFPage, imageData: string): Promise<PDFImage> {
    if (imageData.startsWith('data:image/png;base64,')) {
      const data = Buffer.from(imageData.split(',')[1], 'base64');
      return await page.doc.embedPng(data);
    } else if (imageData.startsWith('data:image/jpeg;base64,')) {
      const data = Buffer.from(imageData.split(',')[1], 'base64');
      return await page.doc.embedJpg(data);
    }
    throw new Error('Unsupported image format');
  }
}
