import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { createHash, createHmac, randomBytes } from 'crypto';
import { Serial } from '../entities/serial.entity';

@Injectable()
export class ValidationService {
  private readonly secretKey: string;
  private readonly algorithms = {
    v1: {
      hash: 'sha256',
      encoding: 'hex',
    },
  };

  constructor(private configService: ConfigService) {
    this.secretKey = this.configService.get<string>('SERIAL_SECRET_KEY');
  }

  async generateSignature(data: Partial<Serial>): Promise<string> {
    const payload = this.preparePayload(data);
    const salt = randomBytes(16).toString('hex');
    const hash = createHmac(this.algorithms.v1.hash, this.secretKey)
      .update(salt + JSON.stringify(payload))
      .digest(this.algorithms.v1.encoding);

    return `${salt}:${hash}`;
  }

  async validateSerial(serial: Serial): Promise<boolean> {
    if (!serial.signature) {
      return false;
    }

    const [salt, storedHash] = serial.signature.split(':');
    if (!salt || !storedHash) {
      return false;
    }

    const payload = this.preparePayload(serial);
    const computedHash = createHmac(this.algorithms.v1.hash, this.secretKey)
      .update(salt + JSON.stringify(payload))
      .digest(this.algorithms.v1.encoding);

    if (computedHash !== storedHash) {
      return false;
    }

    // Additional validations
    if (serial.isDemo) {
      return true;
    }

    if (serial.expirationDate && new Date(serial.expirationDate) < new Date()) {
      return false;
    }

    if (!serial.isActive) {
      return false;
    }

    return true;
  }

  private preparePayload(data: Partial<Serial>): Record<string, any> {
    const { signature, createdAt, updatedAt, deletedAt, ...payload } = data;
    return payload;
  }

  async generateSerialNumber(): Promise<string> {
    const timestamp = Date.now().toString(36);
    const random = randomBytes(8).toString('hex');
    const hash = createHash('sha256')
      .update(timestamp + random + this.secretKey)
      .digest('hex')
      .slice(0, 8);

    return `${timestamp}-${random}-${hash}`.toUpperCase();
  }

  async validateDeviceId(deviceId: string): Promise<boolean> {
    // Add device-specific validation logic
    if (!deviceId || deviceId.length < 10) {
      return false;
    }

    // Add additional device validation rules here
    return true;
  }

  async validateClientNumber(clientNumber: string): Promise<boolean> {
    // Add client number validation logic
    if (!clientNumber || clientNumber.length < 5) {
      return false;
    }

    // Check format (e.g., ABC-12345)
    const clientNumberRegex = /^[A-Z]{3}-\d{5}$/;
    return clientNumberRegex.test(clientNumber);
  }
}
