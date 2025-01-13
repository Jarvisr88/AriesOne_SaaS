import { Test, TestingModule } from '@nestjs/testing';
import { ConfigService } from '@nestjs/config';
import { SerialGeneratorService } from '../../engine/serial-generator.service';
import { EncryptionService } from '../../engine/encryption.service';

describe('SerialGeneratorService', () => {
  let service: SerialGeneratorService;
  let encryptionService: EncryptionService;

  const mockConfigService = {
    get: jest.fn((key: string) => {
      const config = {
        'SERIAL_PRIVATE_KEY': '-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkq...',
        'SERIAL_PUBLIC_KEY': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhki...',
      };
      return config[key];
    }),
  };

  const mockEncryptionService = {
    sign: jest.fn().mockResolvedValue('mock-signature'),
    verify: jest.fn().mockResolvedValue(true),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        SerialGeneratorService,
        {
          provide: ConfigService,
          useValue: mockConfigService,
        },
        {
          provide: EncryptionService,
          useValue: mockEncryptionService,
        },
      ],
    }).compile();

    service = module.get<SerialGeneratorService>(SerialGeneratorService);
    encryptionService = module.get<EncryptionService>(EncryptionService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('generateSerial', () => {
    const testData = {
      clientId: '12345678-abcd-efgh-ijkl-mnopqrstuvwx',
      maxUsageCount: 5,
      expirationDate: new Date('2025-12-31'),
      isDemo: false,
    };

    it('should generate valid serial number', async () => {
      const result = await service.generateSerial(testData);
      
      expect(result.serialNumber).toBeDefined();
      expect(result.signature).toBeDefined();
      expect(result.serialNumber).toContain('-');
      expect(result.serialNumber.split('-').length).toBe(5);
    });

    it('should include client ID in serial number', async () => {
      const result = await service.generateSerial(testData);
      const parts = result.serialNumber.split('-');
      
      expect(parts[2]).toBe(testData.clientId.slice(0, 8));
    });

    it('should sign serial number', async () => {
      await service.generateSerial(testData);
      
      expect(mockEncryptionService.sign).toHaveBeenCalled();
    });
  });

  describe('validateSerial', () => {
    const testSerial = {
      serialNumber: 'ABC123-DEF456-12345678-5-0-0-ABCD',
      signature: 'mock-signature',
    };

    it('should validate correct serial number', async () => {
      const result = await service.validateSerial(
        testSerial.serialNumber,
        testSerial.signature
      );
      
      expect(result.isValid).toBeTruthy();
      expect(result.data).toBeDefined();
    });

    it('should extract metadata correctly', async () => {
      const result = await service.validateSerial(
        testSerial.serialNumber,
        testSerial.signature
      );
      
      expect(result.data).toMatchObject({
        maxUsageCount: expect.any(Number),
        isDemo: expect.any(Boolean),
      });
    });

    it('should fail for invalid signature', async () => {
      mockEncryptionService.verify.mockResolvedValueOnce(false);
      
      const result = await service.validateSerial(
        testSerial.serialNumber,
        'invalid-signature'
      );
      
      expect(result.isValid).toBeFalsy();
    });
  });

  describe('generateDemoSerial', () => {
    it('should generate demo serial with correct parameters', async () => {
      const clientId = '12345678-abcd-efgh-ijkl-mnopqrstuvwx';
      const result = await service.generateDemoSerial(clientId);
      
      expect(result.serialNumber).toBeDefined();
      expect(result.signature).toBeDefined();
      
      const validation = await service.validateSerial(
        result.serialNumber,
        result.signature
      );
      
      expect(validation.isValid).toBeTruthy();
      expect(validation.data.isDemo).toBeTruthy();
      expect(validation.data.maxUsageCount).toBe(1);
    });
  });

  describe('generateBulkSerials', () => {
    const bulkData = {
      clientId: '12345678-abcd-efgh-ijkl-mnopqrstuvwx',
      maxUsageCount: 5,
      expirationDate: new Date('2025-12-31'),
    };

    it('should generate correct number of serials', async () => {
      const count = 3;
      const results = await service.generateBulkSerials(count, bulkData);
      
      expect(results).toHaveLength(count);
      results.forEach(result => {
        expect(result.serialNumber).toBeDefined();
        expect(result.signature).toBeDefined();
      });
    });

    it('should generate unique serials', async () => {
      const count = 5;
      const results = await service.generateBulkSerials(count, bulkData);
      const serialNumbers = results.map(r => r.serialNumber);
      const uniqueSerials = new Set(serialNumbers);
      
      expect(uniqueSerials.size).toBe(count);
    });
  });
});
