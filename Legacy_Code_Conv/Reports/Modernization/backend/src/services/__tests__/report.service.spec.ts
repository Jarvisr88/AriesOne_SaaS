import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ReportService } from '../report.service';
import { Report } from '../../entities/report.entity';
import { CacheService } from '../cache.service';
import { TemplateService } from '../template.service';
import { ExportService } from '../export.service';

describe('ReportService', () => {
  let service: ReportService;
  let reportRepository: Repository<Report>;
  let cacheService: CacheService;
  let templateService: TemplateService;
  let exportService: ExportService;

  const mockReport = {
    id: '1',
    name: 'Test Report',
    description: 'Test Description',
    category: { id: '1', name: 'Test Category' },
    template: { id: '1', name: 'Test Template' },
    parameters: {},
    createdAt: new Date(),
    updatedAt: new Date(),
    createdBy: 'test-user',
    isSystem: false,
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        ReportService,
        {
          provide: getRepositoryToken(Report),
          useValue: {
            find: jest.fn().mockResolvedValue([mockReport]),
            findOne: jest.fn().mockResolvedValue(mockReport),
            save: jest.fn().mockResolvedValue(mockReport),
            create: jest.fn().mockReturnValue(mockReport),
            softDelete: jest.fn().mockResolvedValue(true),
          },
        },
        {
          provide: CacheService,
          useValue: {
            get: jest.fn(),
            set: jest.fn(),
            del: jest.fn(),
          },
        },
        {
          provide: TemplateService,
          useValue: {
            getTemplate: jest.fn().mockResolvedValue({ id: '1', content: 'test' }),
            validateTemplate: jest.fn().mockResolvedValue(true),
          },
        },
        {
          provide: ExportService,
          useValue: {
            exportToPdf: jest.fn().mockResolvedValue(Buffer.from('test')),
            exportToExcel: jest.fn().mockResolvedValue(Buffer.from('test')),
            exportToCsv: jest.fn().mockResolvedValue(Buffer.from('test')),
          },
        },
      ],
    }).compile();

    service = module.get<ReportService>(ReportService);
    reportRepository = module.get<Repository<Report>>(getRepositoryToken(Report));
    cacheService = module.get<CacheService>(CacheService);
    templateService = module.get<TemplateService>(TemplateService);
    exportService = module.get<ExportService>(ExportService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('findAll', () => {
    it('should return an array of reports', async () => {
      const result = await service.findAll({});
      expect(result).toEqual([mockReport]);
      expect(reportRepository.find).toHaveBeenCalled();
    });

    it('should use cache when available', async () => {
      jest.spyOn(cacheService, 'get').mockResolvedValueOnce([mockReport]);
      const result = await service.findAll({});
      expect(result).toEqual([mockReport]);
      expect(cacheService.get).toHaveBeenCalled();
      expect(reportRepository.find).not.toHaveBeenCalled();
    });
  });

  describe('findOne', () => {
    it('should return a single report', async () => {
      const result = await service.findOne('1');
      expect(result).toEqual(mockReport);
      expect(reportRepository.findOne).toHaveBeenCalledWith({
        where: { id: '1' },
        relations: ['category', 'template'],
      });
    });

    it('should throw if report not found', async () => {
      jest.spyOn(reportRepository, 'findOne').mockResolvedValueOnce(null);
      await expect(service.findOne('1')).rejects.toThrow();
    });
  });

  describe('create', () => {
    const createDto = {
      name: 'New Report',
      description: 'New Description',
      categoryId: '1',
      templateId: '1',
      parameters: {},
    };

    it('should create a new report', async () => {
      const result = await service.create(createDto, 'test-user');
      expect(result).toEqual(mockReport);
      expect(reportRepository.create).toHaveBeenCalled();
      expect(reportRepository.save).toHaveBeenCalled();
      expect(cacheService.del).toHaveBeenCalled();
    });

    it('should validate template before creating', async () => {
      await service.create(createDto, 'test-user');
      expect(templateService.validateTemplate).toHaveBeenCalled();
    });
  });

  describe('update', () => {
    const updateDto = {
      name: 'Updated Report',
      description: 'Updated Description',
    };

    it('should update an existing report', async () => {
      const result = await service.update('1', updateDto);
      expect(result).toEqual(mockReport);
      expect(reportRepository.save).toHaveBeenCalled();
      expect(cacheService.del).toHaveBeenCalled();
    });

    it('should throw if updating system report', async () => {
      jest.spyOn(reportRepository, 'findOne').mockResolvedValueOnce({
        ...mockReport,
        isSystem: true,
      });
      await expect(service.update('1', updateDto)).rejects.toThrow();
    });
  });

  describe('delete', () => {
    it('should soft delete a report', async () => {
      await service.delete('1');
      expect(reportRepository.softDelete).toHaveBeenCalledWith('1');
      expect(cacheService.del).toHaveBeenCalled();
    });

    it('should throw if deleting system report', async () => {
      jest.spyOn(reportRepository, 'findOne').mockResolvedValueOnce({
        ...mockReport,
        isSystem: true,
      });
      await expect(service.delete('1')).rejects.toThrow();
    });
  });

  describe('export', () => {
    it('should export to PDF', async () => {
      const result = await service.export('1', 'pdf');
      expect(result).toEqual(Buffer.from('test'));
      expect(exportService.exportToPdf).toHaveBeenCalled();
    });

    it('should export to Excel', async () => {
      const result = await service.export('1', 'excel');
      expect(result).toEqual(Buffer.from('test'));
      expect(exportService.exportToExcel).toHaveBeenCalled();
    });

    it('should export to CSV', async () => {
      const result = await service.export('1', 'csv');
      expect(result).toEqual(Buffer.from('test'));
      expect(exportService.exportToCsv).toHaveBeenCalled();
    });

    it('should throw for invalid format', async () => {
      await expect(service.export('1', 'invalid' as any)).rejects.toThrow();
    });
  });
});
