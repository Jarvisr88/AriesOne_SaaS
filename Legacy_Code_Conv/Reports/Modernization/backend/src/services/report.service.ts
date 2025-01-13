import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Report } from '../entities/report.entity';
import { ReportTemplate } from '../entities/report-template.entity';
import { ReportCategory } from '../entities/report-category.entity';
import { SearchReportsDto, CreateReportDto, UpdateReportDto } from '../dto/report.dto';
import { PaginatedResponse } from '../interfaces/paginated-response.interface';
import { ExportService } from './export.service';
import { CacheService } from './cache.service';

@Injectable()
export class ReportService {
  constructor(
    @InjectRepository(Report)
    private reportRepository: Repository<Report>,
    @InjectRepository(ReportTemplate)
    private templateRepository: Repository<ReportTemplate>,
    @InjectRepository(ReportCategory)
    private categoryRepository: Repository<ReportCategory>,
    private exportService: ExportService,
    private cacheService: CacheService,
  ) {}

  async searchReports(searchDto: SearchReportsDto): Promise<PaginatedResponse<Report>> {
    const cacheKey = `reports:search:${JSON.stringify(searchDto)}`;
    const cached = await this.cacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    const queryBuilder = this.reportRepository.createQueryBuilder('report')
      .leftJoinAndSelect('report.category', 'category')
      .leftJoinAndSelect('report.template', 'template')
      .where('report.isDeleted = :isDeleted', { isDeleted: false });

    if (searchDto.searchText) {
      queryBuilder.andWhere('(report.name ILIKE :search OR report.description ILIKE :search)', {
        search: `%${searchDto.searchText}%`,
      });
    }

    if (searchDto.categoryId) {
      queryBuilder.andWhere('report.categoryId = :categoryId', {
        categoryId: searchDto.categoryId,
      });
    }

    if (searchDto.isSystem !== undefined) {
      queryBuilder.andWhere('report.isSystem = :isSystem', {
        isSystem: searchDto.isSystem,
      });
    }

    const total = await queryBuilder.getCount();
    const items = await queryBuilder
      .orderBy('report.createdAt', 'DESC')
      .skip(searchDto.offset)
      .take(searchDto.limit)
      .getMany();

    const result = {
      items,
      total,
      offset: searchDto.offset,
      limit: searchDto.limit,
    };

    await this.cacheService.set(cacheKey, result, 300); // Cache for 5 minutes
    return result;
  }

  async getReportById(id: string): Promise<Report> {
    const cacheKey = `reports:${id}`;
    const cached = await this.cacheService.get(cacheKey);
    if (cached) {
      return cached;
    }

    const report = await this.reportRepository.findOne({
      where: { id, isDeleted: false },
      relations: ['category', 'template'],
    });

    if (!report) {
      throw new Error('Report not found');
    }

    await this.cacheService.set(cacheKey, report, 300);
    return report;
  }

  async createReport(dto: CreateReportDto, userId: string): Promise<Report> {
    const template = await this.templateRepository.findOneBy({ id: dto.templateId });
    if (!template) {
      throw new Error('Template not found');
    }

    const category = await this.categoryRepository.findOneBy({ id: dto.categoryId });
    if (!category) {
      throw new Error('Category not found');
    }

    const report = this.reportRepository.create({
      ...dto,
      createdBy: userId,
      updatedBy: userId,
    });

    const saved = await this.reportRepository.save(report);
    await this.cacheService.invalidatePattern('reports:*');
    return saved;
  }

  async updateReport(id: string, dto: UpdateReportDto, userId: string): Promise<Report> {
    const report = await this.getReportById(id);

    if (report.isSystem && (dto.name || dto.templateId)) {
      throw new Error('Cannot modify system report name or template');
    }

    if (dto.templateId) {
      const template = await this.templateRepository.findOneBy({ id: dto.templateId });
      if (!template) {
        throw new Error('Template not found');
      }
    }

    if (dto.categoryId) {
      const category = await this.categoryRepository.findOneBy({ id: dto.categoryId });
      if (!category) {
        throw new Error('Category not found');
      }
    }

    Object.assign(report, {
      ...dto,
      updatedBy: userId,
      version: report.version + 1,
    });

    const updated = await this.reportRepository.save(report);
    await this.cacheService.invalidatePattern(`reports:${id}`);
    await this.cacheService.invalidatePattern('reports:search:*');
    return updated;
  }

  async deleteReports(ids: string[], userId: string): Promise<number> {
    const reports = await this.reportRepository.findBy({ id: { $in: ids } });
    const systemReports = reports.filter(r => r.isSystem);
    
    if (systemReports.length > 0) {
      throw new Error('Cannot delete system reports');
    }

    const result = await this.reportRepository.update(
      { id: { $in: ids } },
      {
        isDeleted: true,
        updatedBy: userId,
        updatedAt: new Date(),
      },
    );

    await this.cacheService.invalidatePattern('reports:*');
    return result.affected || 0;
  }

  async cloneReport(id: string, newName: string, userId: string): Promise<Report> {
    const report = await this.getReportById(id);
    const clone = this.reportRepository.create({
      ...report,
      id: undefined,
      name: newName,
      description: `Cloned from ${report.name}`,
      isSystem: false,
      createdBy: userId,
      updatedBy: userId,
      version: 1,
    });

    const saved = await this.reportRepository.save(clone);
    await this.cacheService.invalidatePattern('reports:search:*');
    return saved;
  }

  async exportReport(id: string, format: string, userId: string): Promise<Buffer> {
    const report = await this.getReportById(id);
    return this.exportService.exportReport(report, format, userId);
  }

  async getReportAuditHistory(
    id: string,
    offset = 0,
    limit = 20,
  ): Promise<PaginatedResponse<any>> {
    const result = await this.reportRepository.query(
      'SELECT * FROM get_report_audit_history($1, $2, $3)',
      [id, limit, offset],
    );

    return {
      items: result,
      total: result[0]?.total_count || 0,
      offset,
      limit,
    };
  }
}
