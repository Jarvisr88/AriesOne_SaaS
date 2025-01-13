import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn } from 'typeorm';

@Entity('serial_audits')
export class SerialAudit {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'uuid' })
  entityId: string;

  @Column({ type: 'varchar', length: 50 })
  entityType: 'serial' | 'client' | 'usage';

  @Column({ type: 'varchar', length: 50 })
  action: 'create' | 'update' | 'delete' | 'validate' | 'revoke' | 'renew';

  @Column({ type: 'jsonb' })
  changes: {
    before: Record<string, any>;
    after: Record<string, any>;
  };

  @Column({ type: 'varchar', length: 255, nullable: true })
  ipAddress: string;

  @Column({ type: 'varchar', length: 255, nullable: true })
  userAgent: string;

  @Column({ type: 'varchar', length: 255 })
  performedBy: string;

  @CreateDateColumn()
  performedAt: Date;

  @Column({ type: 'text', nullable: true })
  notes: string;
}
