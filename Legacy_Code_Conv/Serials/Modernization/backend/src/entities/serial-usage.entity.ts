import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Serial } from './serial.entity';

@Entity('serial_usages')
export class SerialUsage {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid' })
  serialId: string;

  @ManyToOne(() => Serial, serial => serial.usages)
  @JoinColumn({ name: 'serialId' })
  serial: Serial;

  @Column({ type: 'varchar', length: 255 })
  deviceId: string;

  @Column({ type: 'inet' })
  ipAddress: string;

  @Column({ type: 'jsonb' })
  deviceInfo: {
    os: string;
    browser: string;
    version: string;
    [key: string]: any;
  };

  @Column({ type: 'varchar', length: 50 })
  status: 'active' | 'expired' | 'revoked';

  @CreateDateColumn()
  createdAt: Date;

  @Column({ nullable: true })
  expiresAt: Date;

  @Column({ type: 'text', nullable: true })
  notes: string;
}
