# Serials Module Deployment Guide

## Overview
This guide provides detailed instructions for deploying the Serials Module in various environments. It covers infrastructure setup, security considerations, and monitoring.

## Infrastructure Requirements

### Hardware Requirements
- **Application Server**
  - CPU: 4 cores minimum
  - RAM: 8GB minimum
  - Storage: 50GB SSD
- **Database Server**
  - CPU: 4 cores minimum
  - RAM: 16GB minimum
  - Storage: 100GB SSD
- **Redis Server**
  - CPU: 2 cores minimum
  - RAM: 4GB minimum
  - Storage: 20GB SSD

### Software Requirements
- **Operating System**
  - Ubuntu 22.04 LTS or higher
- **Runtime**
  - Node.js 18.x or higher
- **Database**
  - PostgreSQL 14.x or higher
- **Cache**
  - Redis 6.x or higher
- **Load Balancer**
  - NGINX 1.20 or higher

## Environment Setup

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl build-essential git

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server
```

### 2. Application Setup
```bash
# Create application directory
sudo mkdir -p /opt/ariesone/serials
sudo chown -R $USER:$USER /opt/ariesone/serials

# Clone repository
git clone https://github.com/ariesone/serials-module.git /opt/ariesone/serials

# Install dependencies
cd /opt/ariesone/serials
npm install --production

# Build application
npm run build
```

### 3. Database Setup
```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE ariesone;
CREATE USER ariesone WITH ENCRYPTED PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE ariesone TO ariesone;
\q

# Run migrations
npm run typeorm migration:run
```

### 4. Redis Setup
```bash
# Configure Redis
sudo nano /etc/redis/redis.conf

# Set password
requirepass your-redis-password

# Restart Redis
sudo systemctl restart redis
```

### 5. NGINX Setup
```bash
# Install NGINX
sudo apt install -y nginx

# Configure NGINX
sudo nano /etc/nginx/sites-available/serials

server {
    listen 80;
    server_name api.ariesone.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/serials /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Security Configuration

### 1. SSL/TLS Setup
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.ariesone.com
```

### 2. Firewall Configuration
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow from 10.0.0.0/8 to any port 5432 # PostgreSQL internal network
sudo ufw allow from 10.0.0.0/8 to any port 6379 # Redis internal network
sudo ufw enable
```

### 3. Key Management
```bash
# Generate keys directory
sudo mkdir -p /opt/ariesone/keys
sudo chown -R $USER:$USER /opt/ariesone/keys

# Generate RSA keys
openssl genrsa -out /opt/ariesone/keys/private.key 4096
openssl rsa -in /opt/ariesone/keys/private.key -pubout -out /opt/ariesone/keys/public.key

# Generate encryption keys
openssl rand -hex 32 > /opt/ariesone/keys/encryption.secret
openssl rand -hex 32 > /opt/ariesone/keys/pepper.secret

# Set permissions
chmod 600 /opt/ariesone/keys/*
```

## Monitoring Setup

### 1. Prometheus Installation
```bash
# Install Prometheus
sudo apt install -y prometheus

# Configure Prometheus
sudo nano /etc/prometheus/prometheus.yml

scrape_configs:
  - job_name: 'serials'
    static_configs:
      - targets: ['localhost:3000']
```

### 2. Grafana Setup
```bash
# Install Grafana
sudo apt install -y grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

### 3. Logging Configuration
```bash
# Install ELK Stack
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt install -y elasticsearch kibana logstash

# Configure Logstash
sudo nano /etc/logstash/conf.d/serials.conf

input {
  file {
    path => "/opt/ariesone/serials/logs/*.log"
    type => "serials"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "serials-%{+YYYY.MM.dd}"
  }
}
```

## Deployment Process

### 1. Environment Variables
Create production environment file:
```bash
nano /opt/ariesone/serials/.env.production

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ariesone
DB_USER=ariesone
DB_PASSWORD=your-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Security
JWT_SECRET=your-jwt-secret
ENCRYPTION_SECRET=your-encryption-secret
ENCRYPTION_PEPPER=your-pepper-value
SERIAL_PRIVATE_KEY=/opt/ariesone/keys/private.key
SERIAL_PUBLIC_KEY=/opt/ariesone/keys/public.key

# API
API_PORT=3000
API_PREFIX=/api/v1
RATE_LIMIT=1000

# Monitoring
PROMETHEUS_PORT=9090
```

### 2. Process Management
Install PM2:
```bash
sudo npm install -g pm2

# Create PM2 config
nano ecosystem.config.js

module.exports = {
  apps: [{
    name: 'serials',
    script: 'dist/main.js',
    instances: 'max',
    exec_mode: 'cluster',
    env_production: {
      NODE_ENV: 'production'
    },
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
}

# Start application
pm2 start ecosystem.config.js --env production
pm2 save
```

### 3. Backup Configuration
Create backup script:
```bash
nano /opt/ariesone/scripts/backup.sh

#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=/opt/ariesone/backups

# Database backup
pg_dump ariesone > $BACKUP_DIR/db_$DATE.sql

# Redis backup
redis-cli save
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Compress backups
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/redis_$DATE.rdb

# Cleanup
rm $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/redis_$DATE.rdb

# Keep last 7 days
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
```

## Maintenance

### 1. Updates
```bash
# Update application
cd /opt/ariesone/serials
git pull
npm install --production
npm run build
pm2 reload all

# Update system
sudo apt update && sudo apt upgrade -y
```

### 2. Monitoring Checks
```bash
# Check application status
pm2 status
pm2 logs

# Check system resources
htop
df -h
free -m

# Check services
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status nginx
```

### 3. Performance Tuning
PostgreSQL configuration:
```bash
sudo nano /etc/postgresql/14/main/postgresql.conf

max_connections = 100
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 512MB
```

Redis configuration:
```bash
sudo nano /etc/redis/redis.conf

maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Troubleshooting

### Common Issues

1. Connection Issues
```bash
# Check service status
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status nginx

# Check logs
tail -f /var/log/postgresql/postgresql-14-main.log
tail -f /var/log/redis/redis-server.log
tail -f /var/log/nginx/error.log
```

2. Performance Issues
```bash
# Check system resources
top
iostat
vmstat

# Check database performance
sudo -u postgres psql
SELECT * FROM pg_stat_activity;
```

3. Backup Issues
```bash
# Check backup status
ls -l /opt/ariesone/backups
tail -f /var/log/cron.log
```

## Support
For additional support:
- Documentation: https://docs.ariesone.com/serials/deployment
- GitHub Issues: https://github.com/ariesone/serials-module/issues
- Email: support@ariesone.com
