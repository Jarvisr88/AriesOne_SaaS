import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { DmercForm } from '../../domain/entities/dmerc-form.entity';
import { DmercFormType } from '../../domain/enums/dmerc-form-type.enum';
import { ValidationService } from './validation.service';
import { CacheService } from '../cache/cache.service';
import { ConfigService } from '../config/config.service';
import { LoggerService } from '../logger/logger.service';
import { NotFoundError, ValidationError } from '../errors';

@Injectable()
export class DmercService {
  private readonly CACHE_TTL = 3600; // 1 hour
  private readonly CACHE_PREFIX = 'dmerc:form:';

  constructor(
    @InjectRepository(DmercForm)
    private readonly formRepository: Repository<DmercForm>,
    private readonly validationService: ValidationService,
    private readonly cacheService: CacheService,
    private readonly configService: ConfigService,
    private readonly logger: LoggerService
  ) {}

  /**
   * Creates a new DMERC form template
   */
  async createForm(form: Partial<DmercForm>): Promise<DmercForm> {
    this.logger.debug('Creating new DMERC form', { type: form.type });

    // Validate form data
    const errors = this.validationService.validateForm(form);
    if (errors.length > 0) {
      throw new ValidationError('Invalid form data', errors);
    }

    // Check for existing active form of same type
    const existingForm = await this.formRepository.findOne({
      where: {
        type: form.type,
        isActive: true
      }
    });

    if (existingForm) {
      // Deactivate existing form
      existingForm.isActive = false;
      existingForm.validTo = new Date();
      await this.formRepository.save(existingForm);
    }

    // Create new form
    const newForm = this.formRepository.create({
      ...form,
      validFrom: new Date(),
      isActive: true
    });

    // Save and cache
    const savedForm = await this.formRepository.save(newForm);
    await this.cacheService.set(
      this.getCacheKey(savedForm.type),
      savedForm,
      this.CACHE_TTL
    );

    return savedForm;
  }

  /**
   * Retrieves a DMERC form by type
   */
  async getForm(type: DmercFormType): Promise<DmercForm> {
    this.logger.debug('Retrieving DMERC form', { type });

    // Check cache first
    const cachedForm = await this.cacheService.get<DmercForm>(
      this.getCacheKey(type)
    );
    if (cachedForm) {
      return cachedForm;
    }

    // Get from database
    const form = await this.formRepository.findOne({
      where: {
        type,
        isActive: true
      }
    });

    if (!form) {
      throw new NotFoundError(`Form not found: ${type}`);
    }

    // Cache for future use
    await this.cacheService.set(
      this.getCacheKey(type),
      form,
      this.CACHE_TTL
    );

    return form;
  }

  /**
   * Updates an existing DMERC form
   */
  async updateForm(
    type: DmercFormType,
    updates: Partial<DmercForm>
  ): Promise<DmercForm> {
    this.logger.debug('Updating DMERC form', { type });

    const form = await this.getForm(type);
    
    // Validate updates
    const errors = this.validationService.validateFormUpdates(updates);
    if (errors.length > 0) {
      throw new ValidationError('Invalid form updates', errors);
    }

    // Apply updates
    Object.assign(form, updates);
    form.updatedAt = new Date();

    // Save and update cache
    const updatedForm = await this.formRepository.save(form);
    await this.cacheService.set(
      this.getCacheKey(type),
      updatedForm,
      this.CACHE_TTL
    );

    return updatedForm;
  }

  /**
   * Validates form data against a form template
   */
  async validateFormData(
    type: DmercFormType,
    data: Record<string, any>
  ): Promise<string[]> {
    this.logger.debug('Validating form data', { type });

    const form = await this.getForm(type);
    return form.validateData(data);
  }

  /**
   * Lists all available form types with their latest versions
   */
  async listForms(): Promise<Array<{ type: DmercFormType; version: string }>> {
    this.logger.debug('Listing all DMERC forms');

    const forms = await this.formRepository.find({
      where: { isActive: true },
      select: ['type', 'version']
    });

    return forms.map(form => ({
      type: form.type,
      version: form.version
    }));
  }

  /**
   * Deactivates a form type
   */
  async deactivateForm(type: DmercFormType): Promise<void> {
    this.logger.debug('Deactivating DMERC form', { type });

    const form = await this.getForm(type);
    form.isActive = false;
    form.validTo = new Date();

    await this.formRepository.save(form);
    await this.cacheService.delete(this.getCacheKey(type));
  }

  /**
   * Gets form history for a specific type
   */
  async getFormHistory(type: DmercFormType): Promise<DmercForm[]> {
    this.logger.debug('Getting form history', { type });

    return this.formRepository.find({
      where: { type },
      order: { validFrom: 'DESC' }
    });
  }

  private getCacheKey(type: DmercFormType): string {
    return `${this.CACHE_PREFIX}${type}`;
  }
}
