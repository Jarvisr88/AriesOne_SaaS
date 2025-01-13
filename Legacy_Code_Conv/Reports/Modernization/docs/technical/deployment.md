# Reports Module Deployment Guide

## Prerequisites

### System Requirements
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose

### Environment Setup
1. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nodejs npm postgresql redis-server docker.io docker-compose

# RHEL/CentOS
sudo yum update
sudo yum install -y nodejs npm postgresql redis docker docker-compose
```

2. Start required services:
```bash
sudo systemctl start postgresql
sudo systemctl start redis
sudo systemctl start docker
```

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd reports-module
```

### 2. Environment Configuration
Create `.env` files for each environment:

```env
# .env.production
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_prod
DB_USER=reports_user
DB_PASSWORD=strong_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# JWT
JWT_SECRET=your_jwt_secret
JWT_EXPIRY=24h

# Export
EXPORT_QUEUE_SIZE=100
EXPORT_TIMEOUT=300
EXPORT_STORAGE_PATH=/var/reports/exports

# API
API_PORT=3000
API_BASE_URL=https://api.example.com
CORS_ORIGIN=https://example.com

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

### 3. Database Setup

1. Create database and user:
```sql
CREATE DATABASE reports_prod;
CREATE USER reports_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE reports_prod TO reports_user;
```

2. Run migrations:
```bash
npm run migration:prod
```

### 4. Build Application

```bash
# Install dependencies
npm install

# Build frontend
cd frontend
npm install
npm run build

# Build backend
cd ../backend
npm install
npm run build
```

## Deployment

### Docker Deployment

1. Build images:
```bash
# Build backend
docker build -t reports-backend -f backend/Dockerfile .

# Build frontend
docker build -t reports-frontend -f frontend/Dockerfile .
```

2. Create docker-compose.yml:
```yaml
version: '3.8'

services:
  backend:
    image: reports-backend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    env_file:
      - .env.production
    depends_on:
      - postgres
      - redis
    networks:
      - reports-network

  frontend:
    image: reports-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - reports-network

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: reports_prod
      POSTGRES_USER: reports_user
      POSTGRES_PASSWORD: strong_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - reports-network

  redis:
    image: redis:6
    command: redis-server --requirepass redis_password
    volumes:
      - redis-data:/data
    networks:
      - reports-network

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - reports-network

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - reports-network

networks:
  reports-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  grafana-data:
```

3. Deploy with Docker Compose:
```bash
docker-compose up -d
```

### Manual Deployment

1. Start backend:
```bash
cd backend
npm run start:prod
```

2. Serve frontend:
```bash
cd frontend/dist
npx serve -s
```

## Monitoring

### Prometheus Configuration
Create `prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'reports-backend'
    static_configs:
      - targets: ['backend:3000']
```

### Grafana Setup

1. Add Prometheus data source:
- URL: http://prometheus:9090
- Access: Server

2. Import dashboards:
- Node.js Application Dashboard
- PostgreSQL Dashboard
- Redis Dashboard

## Backup & Recovery

### Database Backup
```bash
# Backup
pg_dump -U reports_user reports_prod > backup.sql

# Restore
psql -U reports_user reports_prod < backup.sql
```

### Redis Backup
```bash
# Backup
redis-cli -a redis_password save

# Copy dump file
cp /var/lib/redis/dump.rdb backup/
```

## Security Checklist

### SSL/TLS
1. Generate certificates:
```bash
certbot certonly --nginx -d api.example.com
```

2. Configure Nginx:
```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules
```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow PostgreSQL (internal only)
ufw allow from 10.0.0.0/8 to any port 5432
```

## Maintenance

### Log Rotation
Create `/etc/logrotate.d/reports`:
```
/var/log/reports/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 reports reports
    sharedscripts
    postrotate
        systemctl reload reports
    endscript
}
```

### Cleanup Jobs
Create cron jobs:
```bash
# Clean old exports (>7 days)
0 0 * * * find /var/reports/exports -type f -mtime +7 -delete

# Clean audit logs (>90 days)
0 0 * * 0 psql -U reports_user reports_prod -c "DELETE FROM report_audit WHERE performed_at < NOW() - INTERVAL '90 days'"
```

## Troubleshooting

### Common Issues

1. Database Connection Issues:
```bash
# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-14-main.log

# Test connection
psql -U reports_user -h localhost reports_prod
```

2. Redis Connection Issues:
```bash
# Check Redis logs
tail -f /var/log/redis/redis-server.log

# Test connection
redis-cli -a redis_password ping
```

3. Export Generation Issues:
```bash
# Check export service logs
tail -f /var/log/reports/export-service.log

# Check disk space
df -h /var/reports/exports
```

### Health Checks

1. Backend Health:
```bash
curl http://localhost:3000/health
```

2. Database Health:
```bash
psql -U reports_user reports_prod -c "SELECT 1"
```

3. Redis Health:
```bash
redis-cli -a redis_password ping
```
