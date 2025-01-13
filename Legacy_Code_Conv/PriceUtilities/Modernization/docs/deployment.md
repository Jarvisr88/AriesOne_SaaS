# Deployment Guide

## Prerequisites

### System Requirements
- Linux-based OS (Ubuntu 22.04 LTS recommended)
- Docker 24.0+
- Docker Compose 2.20+
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Environment Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd price-utilities-saas
```

2. Create and activate Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Configuration

### Environment Variables

Create `.env` files for both backend and frontend:

#### Backend (.env)
```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=price_utilities
DB_USER=your_user
DB_PASSWORD=your_password

# JWT
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_VERSION=v1
CORS_ORIGINS=http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_AUTH_DOMAIN=your_auth_domain
VITE_AUTH_CLIENT_ID=your_client_id
```

## Database Setup

1. Create PostgreSQL database:
```bash
createdb price_utilities
```

2. Run migrations:
```bash
alembic upgrade head
```

## Development Deployment

### Backend
```bash
# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Start development server
npm run dev
```

## Production Deployment

### Using Docker

1. Build images:
```bash
docker-compose build
```

2. Start services:
```bash
docker-compose up -d
```

### Manual Deployment

#### Backend

1. Install production dependencies:
```bash
pip install gunicorn
```

2. Start backend:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### Frontend

1. Build frontend:
```bash
npm run build
```

2. Serve using Nginx:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Setup Monitoring Tools

1. Install Prometheus:
```bash
docker run -d \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

2. Install Grafana:
```bash
docker run -d \
  -p 3000:3000 \
  grafana/grafana
```

### Health Checks

Monitor the following endpoints:
- `/health`: Basic health check
- `/metrics`: Prometheus metrics
- `/health/live`: Liveness probe
- `/health/ready`: Readiness probe

## Backup and Recovery

### Database Backup
```bash
# Create backup
pg_dump -U your_user price_utilities > backup.sql

# Restore backup
psql -U your_user price_utilities < backup.sql
```

### Log Management
```bash
# Configure log rotation
cat << EOF > /etc/logrotate.d/price_utilities
/var/log/price_utilities/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        systemctl reload price_utilities
    endscript
}
EOF
```

## Troubleshooting

### Common Issues

1. Database Connection Issues
```bash
# Check database status
systemctl status postgresql

# Check connection
psql -U your_user -h localhost -d price_utilities
```

2. API Issues
```bash
# Check API logs
tail -f /var/log/price_utilities/api.log

# Check API status
curl http://localhost:8000/health
```

3. Frontend Issues
```bash
# Clear build cache
rm -rf node_modules/.vite
npm run build

# Check for JavaScript errors
npm run lint
```

### Performance Tuning

1. Database Optimization
```sql
-- Analyze tables
ANALYZE price_list;
ANALYZE audit_log;

-- Update statistics
VACUUM ANALYZE;
```

2. API Optimization
- Enable response compression
- Configure caching headers
- Optimize database queries

3. Frontend Optimization
- Enable code splitting
- Implement lazy loading
- Configure service worker
