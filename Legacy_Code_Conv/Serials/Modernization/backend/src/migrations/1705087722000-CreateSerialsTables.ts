import { MigrationInterface, QueryRunner } from 'typeorm';

export class CreateSerialsTables1705087722000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    // Create clients table
    await queryRunner.query(`
      CREATE TABLE clients (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        client_number VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        metadata JSONB,
        is_active BOOLEAN DEFAULT true,
        contact_email VARCHAR(255),
        contact_phone VARCHAR(50),
        notes TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT now(),
        created_by VARCHAR(255),
        updated_at TIMESTAMP NOT NULL DEFAULT now(),
        updated_by VARCHAR(255),
        deleted_at TIMESTAMP
      );

      CREATE INDEX idx_clients_client_number ON clients(client_number);
      CREATE INDEX idx_clients_is_active ON clients(is_active) WHERE is_active = true;
    `);

    // Create serials table
    await queryRunner.query(`
      CREATE TABLE serials (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        serial_number VARCHAR(255) UNIQUE NOT NULL,
        max_usage_count INTEGER NOT NULL,
        expiration_date TIMESTAMP,
        client_id UUID REFERENCES clients(id),
        metadata JSONB,
        encryption_version VARCHAR(64) NOT NULL,
        signature VARCHAR(255) NOT NULL,
        is_demo BOOLEAN DEFAULT false,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP NOT NULL DEFAULT now(),
        created_by VARCHAR(255),
        updated_at TIMESTAMP NOT NULL DEFAULT now(),
        updated_by VARCHAR(255),
        deleted_at TIMESTAMP
      );

      CREATE INDEX idx_serials_serial_number ON serials(serial_number);
      CREATE INDEX idx_serials_client_id ON serials(client_id);
      CREATE INDEX idx_serials_expiration_date ON serials(expiration_date);
      CREATE INDEX idx_serials_is_active ON serials(is_active) WHERE is_active = true;
    `);

    // Create serial_usages table
    await queryRunner.query(`
      CREATE TABLE serial_usages (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        serial_id UUID REFERENCES serials(id),
        device_id VARCHAR(255) NOT NULL,
        ip_address INET NOT NULL,
        device_info JSONB NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT now(),
        expires_at TIMESTAMP,
        notes TEXT
      );

      CREATE INDEX idx_serial_usages_serial_id ON serial_usages(serial_id);
      CREATE INDEX idx_serial_usages_device_id ON serial_usages(device_id);
      CREATE INDEX idx_serial_usages_status ON serial_usages(status);
    `);

    // Create serial_audits table
    await queryRunner.query(`
      CREATE TABLE serial_audits (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        entity_id UUID NOT NULL,
        entity_type VARCHAR(50) NOT NULL,
        action VARCHAR(50) NOT NULL,
        changes JSONB NOT NULL,
        ip_address VARCHAR(255),
        user_agent VARCHAR(255),
        performed_by VARCHAR(255) NOT NULL,
        performed_at TIMESTAMP NOT NULL DEFAULT now(),
        notes TEXT
      );

      CREATE INDEX idx_serial_audits_entity_id ON serial_audits(entity_id);
      CREATE INDEX idx_serial_audits_entity_type ON serial_audits(entity_type);
      CREATE INDEX idx_serial_audits_performed_at ON serial_audits(performed_at);
    `);

    // Create functions and triggers
    await queryRunner.query(`
      -- Audit trigger function
      CREATE OR REPLACE FUNCTION serial_audit_trigger_func()
      RETURNS TRIGGER AS $$
      DECLARE
        audit_data JSONB;
      BEGIN
        IF (TG_OP = 'DELETE') THEN
          audit_data = jsonb_build_object(
            'before', row_to_json(OLD),
            'after', null
          );
        ELSIF (TG_OP = 'UPDATE') THEN
          audit_data = jsonb_build_object(
            'before', row_to_json(OLD),
            'after', row_to_json(NEW)
          );
        ELSE
          audit_data = jsonb_build_object(
            'before', null,
            'after', row_to_json(NEW)
          );
        END IF;

        INSERT INTO serial_audits (
          entity_id,
          entity_type,
          action,
          changes,
          performed_by
        )
        VALUES (
          COALESCE(NEW.id, OLD.id),
          TG_TABLE_NAME,
          lower(TG_OP),
          audit_data,
          CURRENT_USER
        );

        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;

      -- Create audit triggers
      CREATE TRIGGER serial_audit_trigger
      AFTER INSERT OR UPDATE OR DELETE ON serials
      FOR EACH ROW EXECUTE FUNCTION serial_audit_trigger_func();

      CREATE TRIGGER client_audit_trigger
      AFTER INSERT OR UPDATE OR DELETE ON clients
      FOR EACH ROW EXECUTE FUNCTION serial_audit_trigger_func();

      CREATE TRIGGER usage_audit_trigger
      AFTER INSERT OR UPDATE OR DELETE ON serial_usages
      FOR EACH ROW EXECUTE FUNCTION serial_audit_trigger_func();
    `);
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Drop triggers
    await queryRunner.query(`
      DROP TRIGGER IF EXISTS serial_audit_trigger ON serials;
      DROP TRIGGER IF EXISTS client_audit_trigger ON clients;
      DROP TRIGGER IF EXISTS usage_audit_trigger ON serial_usages;
      DROP FUNCTION IF EXISTS serial_audit_trigger_func();
    `);

    // Drop tables
    await queryRunner.query(`
      DROP TABLE IF EXISTS serial_audits;
      DROP TABLE IF EXISTS serial_usages;
      DROP TABLE IF EXISTS serials;
      DROP TABLE IF EXISTS clients;
    `);
  }
}
