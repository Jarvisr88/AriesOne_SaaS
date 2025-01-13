import { Test, TestingModule } from '@nestjs/testing';
import { ConfigService } from '@nestjs/config';
import { EncryptionService } from '../../engine/encryption.service';

describe('EncryptionService', () => {
  let service: EncryptionService;
  let configService: ConfigService;

  const mockConfigService = {
    get: jest.fn((key: string) => {
      const config = {
        'ENCRYPTION_SECRET': 'test-secret-key-32-chars-exactly!!',
        'ENCRYPTION_PEPPER': 'test-pepper-value',
      };
      return config[key];
    }),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        EncryptionService,
        {
          provide: ConfigService,
          useValue: mockConfigService,
        },
      ],
    }).compile();

    service = module.get<EncryptionService>(EncryptionService);
    configService = module.get<ConfigService>(ConfigService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('encrypt/decrypt', () => {
    it('should encrypt and decrypt data successfully', async () => {
      const testData = 'sensitive-data-123';
      
      const { encrypted, version } = await service.encrypt(testData);
      expect(encrypted).toBeDefined();
      expect(version).toBe('v1');

      const decrypted = await service.decrypt(encrypted, version);
      expect(decrypted).toBe(testData);
    });

    it('should throw error for invalid version', async () => {
      const testData = 'test-data';
      const { encrypted } = await service.encrypt(testData);

      await expect(service.decrypt(encrypted, 'v2')).rejects.toThrow(
        'Unsupported encryption version: v2'
      );
    });
  });

  describe('hash/verify', () => {
    it('should hash and verify data successfully', async () => {
      const testData = 'password123';
      
      const hashedData = await service.hash(testData);
      expect(hashedData).toBeDefined();
      expect(hashedData.includes(':')).toBeTruthy();

      const isValid = await service.verify(testData, hashedData);
      expect(isValid).toBeTruthy();
    });

    it('should return false for invalid data', async () => {
      const testData = 'password123';
      const wrongData = 'password124';
      
      const hashedData = await service.hash(testData);
      const isValid = await service.verify(wrongData, hashedData);
      
      expect(isValid).toBeFalsy();
    });
  });

  describe('digital signatures', () => {
    it('should generate valid key pair', async () => {
      const { publicKey, privateKey } = await service.generateKeyPair();
      
      expect(publicKey).toBeDefined();
      expect(privateKey).toBeDefined();
      expect(publicKey).toContain('BEGIN PUBLIC KEY');
      expect(privateKey).toContain('BEGIN PRIVATE KEY');
    });

    it('should sign and verify data successfully', async () => {
      const testData = 'message-to-sign';
      const { publicKey, privateKey } = await service.generateKeyPair();
      
      const signature = await service.sign(testData, privateKey);
      expect(signature).toBeDefined();

      const isValid = await service.verify(testData, signature, publicKey);
      expect(isValid).toBeTruthy();
    });

    it('should fail verification for tampered data', async () => {
      const testData = 'original-message';
      const tamperedData = 'tampered-message';
      const { publicKey, privateKey } = await service.generateKeyPair();
      
      const signature = await service.sign(testData, privateKey);
      const isValid = await service.verify(tamperedData, signature, publicKey);
      
      expect(isValid).toBeFalsy();
    });
  });

  describe('error handling', () => {
    it('should handle encryption errors gracefully', async () => {
      jest.spyOn(configService, 'get').mockReturnValueOnce(null);
      
      await expect(service.encrypt('test')).rejects.toThrow();
    });

    it('should handle decryption errors gracefully', async () => {
      await expect(service.decrypt('invalid-data', 'v1')).rejects.toThrow();
    });
  });
});
