import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import {
  createCipheriv,
  createDecipheriv,
  createHash,
  randomBytes,
  scrypt,
} from 'crypto';
import { promisify } from 'util';

@Injectable()
export class EncryptionService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly keyLength = 32;
  private readonly ivLength = 16;
  private readonly saltLength = 64;
  private readonly tagLength = 16;
  private readonly secret: string;
  private readonly pepper: string;

  constructor(private configService: ConfigService) {
    this.secret = this.configService.get<string>('ENCRYPTION_SECRET');
    this.pepper = this.configService.get<string>('ENCRYPTION_PEPPER');
  }

  async encrypt(data: string): Promise<{
    encrypted: string;
    version: string;
  }> {
    try {
      const salt = randomBytes(this.saltLength);
      const iv = randomBytes(this.ivLength);
      const key = await this.deriveKey(salt);

      const cipher = createCipheriv(this.algorithm, key, iv, {
        authTagLength: this.tagLength,
      });

      const encrypted = Buffer.concat([
        cipher.update(data, 'utf8'),
        cipher.final(),
      ]);

      const authTag = cipher.getAuthTag();

      const result = Buffer.concat([
        salt,
        iv,
        authTag,
        encrypted,
      ]).toString('base64');

      return {
        encrypted: result,
        version: 'v1',
      };
    } catch (error) {
      throw new Error(`Encryption failed: ${error.message}`);
    }
  }

  async decrypt(encrypted: string, version: string): Promise<string> {
    if (version !== 'v1') {
      throw new Error(`Unsupported encryption version: ${version}`);
    }

    try {
      const data = Buffer.from(encrypted, 'base64');

      const salt = data.slice(0, this.saltLength);
      const iv = data.slice(this.saltLength, this.saltLength + this.ivLength);
      const authTag = data.slice(
        this.saltLength + this.ivLength,
        this.saltLength + this.ivLength + this.tagLength
      );
      const encryptedText = data.slice(this.saltLength + this.ivLength + this.tagLength);

      const key = await this.deriveKey(salt);

      const decipher = createDecipheriv(this.algorithm, key, iv, {
        authTagLength: this.tagLength,
      });
      decipher.setAuthTag(authTag);

      const decrypted = Buffer.concat([
        decipher.update(encryptedText),
        decipher.final(),
      ]);

      return decrypted.toString('utf8');
    } catch (error) {
      throw new Error(`Decryption failed: ${error.message}`);
    }
  }

  async hash(data: string): Promise<string> {
    const salt = randomBytes(this.saltLength);
    const hash = createHash('sha512')
      .update(salt)
      .update(data)
      .update(this.pepper)
      .digest('hex');

    return `${salt.toString('hex')}:${hash}`;
  }

  async verify(data: string, hashedData: string): Promise<boolean> {
    const [salt, storedHash] = hashedData.split(':');
    const hash = createHash('sha512')
      .update(Buffer.from(salt, 'hex'))
      .update(data)
      .update(this.pepper)
      .digest('hex');

    return storedHash === hash;
  }

  private async deriveKey(salt: Buffer): Promise<Buffer> {
    const scryptAsync = promisify(scrypt);
    return scryptAsync(this.secret, salt, this.keyLength) as Promise<Buffer>;
  }

  async generateKeyPair(): Promise<{
    publicKey: string;
    privateKey: string;
  }> {
    const { generateKeyPairSync } = await import('crypto');
    const { publicKey, privateKey } = generateKeyPairSync('rsa', {
      modulusLength: 4096,
      publicKeyEncoding: {
        type: 'spki',
        format: 'pem',
      },
      privateKeyEncoding: {
        type: 'pkcs8',
        format: 'pem',
      },
    });

    return { publicKey, privateKey };
  }

  async sign(data: string, privateKey: string): Promise<string> {
    const { createSign } = await import('crypto');
    const sign = createSign('SHA512');
    sign.update(data);
    return sign.sign(privateKey, 'base64');
  }

  async verify(data: string, signature: string, publicKey: string): Promise<boolean> {
    const { createVerify } = await import('crypto');
    const verify = createVerify('SHA512');
    verify.update(data);
    return verify.verify(publicKey, signature, 'base64');
  }
}
