# AriesOne Data Module Setup Guide

## Prerequisites

### System Requirements
- Python 3.11 or higher
- PostgreSQL 15.0 or higher
- Redis 7.0 or higher
- Docker 24.0 or higher
- Docker Compose 2.20 or higher

### Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/ariesone/saas.git
cd saas
```

### 2. Configure Environment
Create `.env` file in project root:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ariesone
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
CORS_ORIGINS=["http://localhost:3000"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### 3. Database Setup
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Load initial data
python scripts/seed_data.py
```

### 4. Cache Setup
```bash
# Start Redis
docker-compose up -d redis

# Verify connection
redis-cli ping
```

### 5. Message Queue Setup
```bash
# Start RabbitMQ
docker-compose up -d rabbitmq

# Verify connection
rabbitmqctl status
```

## Development Setup

### 1. Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 2. IDE Configuration
#### VSCode Settings
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.analysis.typeCheckingMode": "strict"
}
```

### 3. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks
pre-commit run --all-files
```

## Running the Application

### 1. Development Mode
```bash
# Start all services
docker-compose up -d

# Run API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Production Mode
```bash
# Build containers
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Testing
```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run all tests with coverage
pytest --cov=app tests/
```

## Health Checks

### 1. API Health
```bash
curl http://localhost:8000/health
```

### 2. Database Health
```bash
curl http://localhost:8000/health/db
```

### 3. Cache Health
```bash
curl http://localhost:8000/health/cache
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
alembic upgrade head
```

#### 2. Cache Connection Issues
```bash
# Check Redis status
docker-compose ps redis

# View Redis logs
docker-compose logs redis

# Flush Redis
redis-cli flushall
```

#### 3. API Server Issues
```bash
# Check logs
tail -f logs/api.log

# Restart server
docker-compose restart api
```

## Maintenance

### 1. Backup
```bash
# Backup database
pg_dump -U user -d ariesone > backup.sql

# Backup Redis
redis-cli save
```

### 2. Monitoring
```bash
# View API metrics
curl http://localhost:8000/metrics

# View container stats
docker stats
```

### 3. Logging
```bash
# View combined logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
```

## Security

### 1. SSL/TLS Setup
```bash
# Generate certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout private.key -out certificate.crt

# Configure Nginx
cp nginx/ssl.conf /etc/nginx/conf.d/
```

### 2. Firewall Rules
```bash
# Allow API port
ufw allow 8000

# Allow PostgreSQL
ufw allow 5432

# Allow Redis
ufw allow 6379
```

## Support

For additional support:
- GitHub Issues: https://github.com/ariesone/saas/issues
- Documentation: https://docs.ariesone.com
- Email: support@ariesone.com
