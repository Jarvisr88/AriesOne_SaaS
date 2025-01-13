import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { randomBytes, createHash } from 'crypto';
import { EncryptionService } from './encryption.service';

@Injectable()
export class SerialGeneratorService {
  private readonly serialLength = 20;
  private readonly checksumLength = 4;
  private readonly privateKey: string;
  private readonly publicKey: string;

  constructor(
    private configService: ConfigService,
    private encryptionService: EncryptionService,
  ) {
    this.privateKey = this.configService.get<string>('SERIAL_PRIVATE_KEY');
    this.publicKey = this.configService.get<string>('SERIAL_PUBLIC_KEY');
  }

  async generateSerial(data: {
    clientId: string;
    maxUsageCount: number;
    expirationDate?: Date;
    isDemo?: boolean;
  }): Promise<{
    serialNumber: string;
    signature: string;
  }> {
    // Generate base components
    const timestamp = Date.now().toString(36);
    const random = randomBytes(8).toString('hex');
    const clientPart = data.clientId.slice(0, 8);

    // Create metadata string
    const metadata = [
      data.maxUsageCount.toString(36),
      data.expirationDate ? data.expirationDate.getTime().toString(36) : '0',
      data.isDemo ? '1' : '0',
    ].join('-');

    // Generate checksum
    const checksum = this.generateChecksum(
      timestamp,
      random,
      clientPart,
      metadata
    );

    // Combine all parts
    const serialNumber = [
      timestamp,
      random,
      clientPart,
      metadata,
      checksum,
    ].join('-').toUpperCase();

    // Sign the serial
    const signature = await this.encryptionService.sign(
      serialNumber,
      this.privateKey
    );

    return {
      serialNumber,
      signature,
    };
  }

  async validateSerial(
    serialNumber: string,
    signature: string
  ): Promise<{
    isValid: boolean;
    data?: {
      timestamp: number;
      clientId: string;
      maxUsageCount: number;
      expirationDate?: Date;
      isDemo: boolean;
    };
  }> {
    try {
      // Verify signature
      const isSignatureValid = await this.encryptionService.verify(
        serialNumber,
        signature,
        this.publicKey
      );

      if (!isSignatureValid) {
        return { isValid: false };
      }

      // Parse serial number
      const [timestamp, random, clientPart, metadata, checksum] = serialNumber.split('-');

      // Verify checksum
      const expectedChecksum = this.generateChecksum(
        timestamp,
        random,
        clientPart,
        metadata
      );

      if (checksum !== expectedChecksum) {
        return { isValid: false };
      }

      // Parse metadata
      const [maxUsageCount, expirationTimestamp, isDemo] = metadata.split('-');

      return {
        isValid: true,
        data: {
          timestamp: parseInt(timestamp, 36),
          clientId: clientPart,
          maxUsageCount: parseInt(maxUsageCount, 36),
          expirationDate: expirationTimestamp !== '0'
            ? new Date(parseInt(expirationTimestamp, 36))
            : undefined,
          isDemo: isDemo === '1',
        },
      };
    } catch (error) {
      return { isValid: false };
    }
  }

  private generateChecksum(...parts: string[]): string {
    const data = parts.join('');
    return createHash('sha256')
      .update(data)
      .digest('hex')
      .slice(0, this.checksumLength)
      .toUpperCase();
  }

  async generateDemoSerial(clientId: string): Promise<{
    serialNumber: string;
    signature: string;
  }> {
    return this.generateSerial({
      clientId,
      maxUsageCount: 1,
      expirationDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 days
      isDemo: true,
    });
  }

  async generateBulkSerials(
    count: number,
    data: {
      clientId: string;
      maxUsageCount: number;
      expirationDate?: Date;
    }
  ): Promise<Array<{ serialNumber: string; signature: string }>> {
    const serials = [];
    for (let i = 0; i < count; i++) {
      const serial = await this.generateSerial(data);
      serials.push(serial);
    }
    return serials;
  }
}
