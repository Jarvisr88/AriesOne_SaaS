import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn, DeleteDateColumn, ManyToOne, OneToMany, JoinColumn } from 'typeorm';
import { Client } from './client.entity';
import { SerialUsage } from './serial-usage.entity';

@Entity('serials')
export class Serial {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ length: 255, unique: true })
  serialNumber: string;

  @Column({ type: 'int' })
  maxUsageCount: number;

  @Column({ type: 'timestamp', nullable: true })
  expirationDate: Date;

  @Column({ type: 'uuid' })
  clientId: string;

  @ManyToOne(() => Client, client => client.serials)
  @JoinColumn({ name: 'clientId' })
  client: Client;

  @OneToMany(() => SerialUsage, usage => usage.serial)
  usages: SerialUsage[];

  @Column({ type: 'jsonb', nullable: true })
  metadata: Record<string, any>;

  @Column({ type: 'varchar', length: 64 })
  encryptionVersion: string;

  @Column({ type: 'varchar', length: 255 })
  signature: string;

  @Column({ default: false })
  isDemo: boolean;

  @Column({ default: true })
  isActive: boolean;

  @CreateDateColumn()
  createdAt: Date;

  @Column({ nullable: true })
  createdBy: string;

  @UpdateDateColumn()
  updatedAt: Date;

  @Column({ nullable: true })
  updatedBy: string;

  @DeleteDateColumn()
  deletedAt: Date;
}
