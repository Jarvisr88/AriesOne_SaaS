import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { SerialController } from '../../controllers/serial.controller';
import { SerialService } from '../../services/serial.service';
import { Serial } from '../../entities/serial.entity';
import { CreateSerialDto, UpdateSerialDto } from '../../dto/serial.dto';
import { JwtAuthGuard } from '../../guards/jwt-auth.guard';
import { RolesGuard } from '../../guards/roles.guard';

describe('SerialController (Integration)', () => {
  let app: INestApplication;
  let serialRepository: Repository<Serial>;
  let jwtToken: string;

  const mockSerial = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    serialNumber: 'TEST123-456',
    maxUsageCount: 5,
    isActive: true,
    isDemo: false,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockSerialService = {
    create: jest.fn().mockResolvedValue(mockSerial),
    findAll: jest.fn().mockResolvedValue([[mockSerial], 1]),
    findOne: jest.fn().mockResolvedValue(mockSerial),
    update: jest.fn().mockResolvedValue(mockSerial),
    delete: jest.fn().mockResolvedValue(undefined),
    validate: jest.fn().mockResolvedValue(true),
  };

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [SerialController],
      providers: [
        {
          provide: SerialService,
          useValue: mockSerialService,
        },
        {
          provide: getRepositoryToken(Serial),
          useClass: Repository,
        },
      ],
    })
      .overrideGuard(JwtAuthGuard)
      .useValue({ canActivate: () => true })
      .overrideGuard(RolesGuard)
      .useValue({ canActivate: () => true })
      .compile();

    app = moduleFixture.createNestApplication();
    serialRepository = moduleFixture.get<Repository<Serial>>(
      getRepositoryToken(Serial)
    );
    
    // Setup mock JWT token
    jwtToken = 'mock.jwt.token';
    
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('POST /serials', () => {
    const createSerialDto: CreateSerialDto = {
      clientId: '123e4567-e89b-12d3-a456-426614174000',
      maxUsageCount: 5,
      expirationDate: new Date('2025-12-31'),
      isDemo: false,
    };

    it('should create a new serial', () => {
      return request(app.getHttpServer())
        .post('/serials')
        .set('Authorization', `Bearer ${jwtToken}`)
        .send(createSerialDto)
        .expect(201)
        .expect(res => {
          expect(res.body).toMatchObject({
            id: expect.any(String),
            serialNumber: expect.any(String),
            maxUsageCount: createSerialDto.maxUsageCount,
          });
        });
    });

    it('should validate request body', () => {
      const invalidDto = { ...createSerialDto, maxUsageCount: -1 };
      
      return request(app.getHttpServer())
        .post('/serials')
        .set('Authorization', `Bearer ${jwtToken}`)
        .send(invalidDto)
        .expect(400);
    });
  });

  describe('GET /serials', () => {
    it('should return paginated serials', () => {
      return request(app.getHttpServer())
        .get('/serials')
        .set('Authorization', `Bearer ${jwtToken}`)
        .expect(200)
        .expect(res => {
          expect(res.body).toMatchObject({
            data: expect.any(Array),
            total: expect.any(Number),
          });
        });
    });

    it('should handle pagination parameters', () => {
      return request(app.getHttpServer())
        .get('/serials?offset=10&limit=5')
        .set('Authorization', `Bearer ${jwtToken}`)
        .expect(200)
        .expect(res => {
          expect(res.body.offset).toBe(10);
          expect(res.body.limit).toBe(5);
        });
    });
  });

  describe('GET /serials/:id', () => {
    it('should return serial by id', () => {
      return request(app.getHttpServer())
        .get(`/serials/${mockSerial.id}`)
        .set('Authorization', `Bearer ${jwtToken}`)
        .expect(200)
        .expect(res => {
          expect(res.body).toMatchObject(mockSerial);
        });
    });

    it('should handle non-existent serial', () => {
      mockSerialService.findOne.mockRejectedValueOnce(new Error('Not found'));
      
      return request(app.getHttpServer())
        .get('/serials/non-existent-id')
        .set('Authorization', `Bearer ${jwtToken}`)
        .expect(404);
    });
  });

  describe('PUT /serials/:id', () => {
    const updateSerialDto: UpdateSerialDto = {
      maxUsageCount: 10,
      isActive: true,
    };

    it('should update serial', () => {
      return request(app.getHttpServer())
        .put(`/serials/${mockSerial.id}`)
        .set('Authorization', `Bearer ${jwtToken}`)
        .send(updateSerialDto)
        .expect(200)
        .expect(res => {
          expect(res.body).toMatchObject({
            ...mockSerial,
            maxUsageCount: updateSerialDto.maxUsageCount,
          });
        });
    });
  });

  describe('DELETE /serials/:id', () => {
    it('should delete serial', () => {
      return request(app.getHttpServer())
        .delete(`/serials/${mockSerial.id}`)
        .set('Authorization', `Bearer ${jwtToken}`)
        .expect(204);
    });
  });

  describe('POST /serials/validate', () => {
    const validateDto = {
      serialNumber: 'TEST123-456',
      deviceId: 'device123',
      deviceInfo: { os: 'linux', version: '1.0' },
    };

    it('should validate serial', () => {
      return request(app.getHttpServer())
        .post('/serials/validate')
        .send(validateDto)
        .expect(200)
        .expect(res => {
          expect(res.body).toBe(true);
        });
    });
  });

  describe('Error Handling', () => {
    it('should handle unauthorized access', () => {
      return request(app.getHttpServer())
        .get('/serials')
        .expect(401);
    });

    it('should handle validation errors', () => {
      const invalidDto = { maxUsageCount: 'invalid' };
      
      return request(app.getHttpServer())
        .post('/serials')
        .set('Authorization', `Bearer ${jwtToken}`)
        .send(invalidDto)
        .expect(400);
    });

    it('should handle database errors', () => {
      mockSerialService.create.mockRejectedValueOnce(new Error('DB Error'));
      
      return request(app.getHttpServer())
        .post('/serials')
        .set('Authorization', `Bearer ${jwtToken}`)
        .send({
          clientId: '123',
          maxUsageCount: 5,
        })
        .expect(500);
    });
  });
});
