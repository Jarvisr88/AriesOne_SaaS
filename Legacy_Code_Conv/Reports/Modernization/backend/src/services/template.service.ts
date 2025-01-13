import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ReportTemplate } from '../entities/report-template.entity';
import { CreateTemplateDto, UpdateTemplateDto } from '../dto/template.dto';
import { PaginatedResponse } from '../interfaces/paginated-response.interface';
import { CacheService } from './cache.service';

@Injectable()
export class TemplateService {
  constructor(
    @InjectRepository(ReportTemplate)
    private templateRepository: Repository<ReportTemplate>,
    private cacheService: CacheService,
  ) {}

  async getTemplates(
    type?: string,
    offset = 0,
    limit = 20,
  ): Promise<PaginatedResponse<ReportTemplate>> {
    const cacheKey = `templates:list:${type}:${offset}:${limit}`;
    const cached = await this.cacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    const queryBuilder = this.templateRepository.createQueryBuilder('template')
      .where('template.isActive = :isActive', { isActive: true });

    if (type) {
      queryBuilder.andWhere('template.templateType = :type', { type });
    }

    const total = await queryBuilder.getCount();
    const items = await queryBuilder
      .orderBy('template.name', 'ASC')
      .skip(offset)
      .take(limit)
      .getMany();

    const result = { items, total, offset, limit };
    await this.cacheService.set(cacheKey, result, 300);
    return result;
  }

  async getTemplateById(id: string): Promise<ReportTemplate> {
    const cacheKey = `templates:${id}`;
    const cached = await this.cacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    const template = await this.templateRepository.findOne({
      where: { id, isActive: true },
    });

    if (!template) {
      throw new Error('Template not found');
    }

    await this.cacheService.set(cacheKey, template, 300);
    return template;
  }

  async createTemplate(dto: CreateTemplateDto, userId: string): Promise<ReportTemplate> {
    const template = this.templateRepository.create({
      ...dto,
      version: 1,
      createdBy: userId,
      updatedBy: userId,
    });

    const saved = await this.templateRepository.save(template);
    await this.cacheService.invalidatePattern('templates:*');
    return saved;
  }

  async updateTemplate(
    id: string,
    dto: UpdateTemplateDto,
    userId: string,
  ): Promise<ReportTemplate> {
    const template = await this.getTemplateById(id);

    Object.assign(template, {
      ...dto,
      version: template.version + 1,
      updatedBy: userId,
    });

    const updated = await this.templateRepository.save(template);
    await this.cacheService.invalidatePattern(`templates:${id}`);
    await this.cacheService.invalidatePattern('templates:list:*');
    return updated;
  }

  async deleteTemplate(id: string): Promise<void> {
    const template = await this.getTemplateById(id);
    
    // Check if template is in use
    const usageCount = await this.templateRepository
      .createQueryBuilder('template')
      .leftJoin('template.reports', 'report')
      .where('template.id = :id', { id })
      .andWhere('report.isDeleted = false')
      .getCount();

    if (usageCount > 0) {
      throw new Error('Template is in use by active reports');
    }

    template.isActive = false;
    await this.templateRepository.save(template);
    await this.cacheService.invalidatePattern('templates:*');
  }

  async validateTemplate(templateData: any): Promise<boolean> {
    // Implement template validation logic based on type
    try {
      switch (templateData.type) {
        case 'pdf':
          return this.validatePdfTemplate(templateData);
        case 'excel':
          return this.validateExcelTemplate(templateData);
        default:
          throw new Error('Unsupported template type');
      }
    } catch (error) {
      throw new Error(`Template validation failed: ${error.message}`);
    }
  }

  private validatePdfTemplate(templateData: any): boolean {
    const requiredFields = ['format', 'orientation', 'margins'];
    for (const field of requiredFields) {
      if (!templateData[field]) {
        throw new Error(`Missing required field: ${field}`);
      }
    }
    return true;
  }

  private validateExcelTemplate(templateData: any): boolean {
    if (!Array.isArray(templateData.sheets) || templateData.sheets.length === 0) {
      throw new Error('Excel template must have at least one sheet');
    }
    return true;
  }
}
