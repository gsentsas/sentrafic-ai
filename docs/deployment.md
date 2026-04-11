# SEN TRAFIC AI - Deployment Guide

## Prerequisites

### System Requirements

- **CPU**: 4 cores minimum (8 recommended for production)
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 50GB SSD (for data and logs)
- **GPU**: NVIDIA GPU with CUDA 11.0+ (optional, for faster inference)
- **Network**: Stable internet connection, fixed IP address recommended

### Software Requirements

- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Docker**: 20.10+ (with docker-compose 1.29+)
- **Docker Compose**: 2.0+ (standalone installation)
- **SSL Certificate**: Valid SSL/TLS certificate (for HTTPS)
- **Domain Name**: Registered domain for your instance
- **Reverse Proxy**: Nginx or HAProxy (for production)

## VPS Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Set timezone (change to your timezone)
sudo timedatectl set-timezone Africa/Dakar

# Create application user
sudo useradd -m -s /bin/bash sentrafic

# Add user to docker group (avoid using sudo for docker)
sudo usermod -aG docker sentrafic

# Switch to application user
sudo su - sentrafic
```

### 2. Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify Docker installation
docker --version

# Install Docker Compose (if not included)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify Docker Compose
docker-compose --version
```

### 3. Install NVIDIA Docker (Optional - for GPU Support)

```bash
# Install NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 4. Setup Application Directory

```bash
# Create application directories
mkdir -p ~/sen-trafic-ai
mkdir -p ~/sen-trafic-ai/data/postgres
mkdir -p ~/sen-trafic-ai/data/redis
mkdir -p ~/sen-trafic-ai/logs

# Set proper permissions
chmod 700 ~/sen-trafic-ai/data

# Clone or download the application
cd ~/sen-trafic-ai
# git clone <repo-url> .
```

## Docker Deployment

### 1. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit environment file with production values
nano .env
```

**Critical .env settings for production**:

```env
# Database - Use strong password!
POSTGRES_USER=sentrafic
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE
POSTGRES_DB=sentrafic
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis - Consider adding password
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@redis:6379/0

# JWT Secret - Generate a strong random key
JWT_SECRET=YOUR_STRONG_RANDOM_SECRET_KEY_HERE

# Frontend URL
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Security
SECURE_COOKIES=true
APP_DEBUG=false
APP_ENVIRONMENT=production

# Email (for alerts)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**Generate strong secrets**:

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate database password
openssl rand -base64 32
```

### 2. Production Docker Compose Configuration

Create `docker-compose.prod.yml` for production-specific settings:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: sentrafic-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - sentrafic-net
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    container_name: sentrafic-redis
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - sentrafic-net
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M

  backend-api:
    build:
      context: ./backend-api
      dockerfile: Dockerfile
    container_name: sentrafic-backend
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_HOST: postgres
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET: ${JWT_SECRET}
      APP_DEBUG: false
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
    networks:
      - sentrafic-net
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "10"

  vision-engine:
    build:
      context: ./vision-engine
      dockerfile: Dockerfile
    container_name: sentrafic-vision
    environment:
      VISION_BACKEND_URL: http://backend-api:8000
      VISION_USE_GPU: true
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    networks:
      - sentrafic-net

  dashboard:
    build:
      context: ./dashboard
      dockerfile: Dockerfile
    container_name: sentrafic-dashboard
    environment:
      NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
    networks:
      - sentrafic-net

volumes:
  postgres_data:
  redis_data:

networks:
  sentrafic-net:
    driver: bridge
```

### 3. Deploy Services

```bash
# Start services in detached mode
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## SSL/TLS Configuration

### 1. Obtain SSL Certificate

**Using Let's Encrypt with Certbot**:

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot certonly --standalone -d api.yourdomain.com -d yourdomain.com

# Verify certificate
sudo certbot certificates
```

Certificates are stored in `/etc/letsencrypt/live/yourdomain.com/`

### 2. Nginx Reverse Proxy Configuration

Create `/etc/nginx/sites-available/sentrafic`:

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name api.yourdomain.com yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;
    gzip_min_length 1000;

    # Proxy to backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }

    # Proxy to documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://localhost:8000/redoc;
        proxy_set_header Host $host;
    }

    # Return 404 for health checks on dashboard
    location /health {
        return 404;
    }
}

# HTTPS Dashboard
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;

    # Proxy to dashboard
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/sentrafic /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 3. Auto-Renew SSL Certificates

```bash
# Test renewal
sudo certbot renew --dry-run

# Create systemd timer for auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check status
sudo systemctl status certbot.timer
```

## Database Backup & Recovery

### 1. Automated Backups

Create `/home/sentrafic/backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/sentrafic/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
BACKUP_FILE="$BACKUP_DIR/postgres_backup_$TIMESTAMP.sql.gz"
docker-compose exec -T postgres pg_dump \
  -U sentrafic sentrafic | gzip > $BACKUP_FILE

# Keep only recent backups
find $BACKUP_DIR -name "postgres_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"

# Optional: Upload to cloud storage
# aws s3 cp $BACKUP_FILE s3://your-bucket/backups/
```

Make executable and add to crontab:

```bash
chmod +x /home/sentrafic/backup-db.sh

# Run daily at 2 AM
(crontab -l; echo "0 2 * * * /home/sentrafic/backup-db.sh") | crontab -
```

### 2. Restore from Backup

```bash
# Stop containers
docker-compose down

# Restore database
docker-compose up -d postgres
sleep 10

# Restore backup
zcat /path/to/backup.sql.gz | docker-compose exec -T postgres psql -U sentrafic sentrafic

# Restart all services
docker-compose up -d
```

## Monitoring & Logging

### 1. View Logs

```bash
# View all service logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend-api

# View last 100 lines
docker-compose logs --tail 100 backend-api
```

### 2. System Monitoring

```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Monitor in real-time
watch -n 1 'docker stats --no-stream'
```

### 3. Centralized Logging (Optional)

For production, consider using ELK Stack or Cloud providers:

```yaml
# Add to docker-compose for centralized logging
services:
  backend-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "10"
        labels: "service=backend-api,environment=production"
```

## Performance Tuning

### 1. PostgreSQL Optimization

Access PostgreSQL container:

```bash
docker-compose exec postgres bash

# Connect to database
psql -U sentrafic sentrafic

# Check configuration
SHOW shared_buffers;
SHOW effective_cache_size;
SHOW work_mem;

# Exit
\q
```

Update `postgresql.conf` for better performance:

```
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 64MB
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2. Redis Optimization

Configure in docker-compose:

```yaml
redis:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru --save 60 1000
```

### 3. Backend API Scaling

Update docker-compose for multiple instances:

```yaml
backend-api:
  deploy:
    replicas: 3
```

Use load balancer (Nginx or HAProxy) to distribute traffic.

## Security Hardening

### 1. Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block all other ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### 2. Fail2Ban Installation

```bash
# Install Fail2Ban
sudo apt-get install fail2ban -y

# Enable service
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Security Updates

```bash
# Enable automatic updates
sudo apt-get install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs backend-api

# Rebuild container
docker-compose build --no-cache backend-api

# Restart all services
docker-compose restart
```

### Database Connection Issues

```bash
# Test PostgreSQL connectivity
docker-compose exec backend-api psql -h postgres -U sentrafic -d sentrafic -c "SELECT 1"

# Check PostgreSQL logs
docker-compose logs postgres
```

### High CPU/Memory Usage

```bash
# Monitor resource usage
docker stats

# Check database query performance
docker-compose exec postgres psql -U sentrafic sentrafic -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10"
```

### Vision Engine Not Processing

```bash
# Check GPU availability
docker-compose exec vision-engine nvidia-smi

# Check vision logs
docker-compose logs vision-engine

# Verify backend connectivity
docker-compose exec vision-engine curl http://backend-api:8000/api/health
```

## Maintenance

### Regular Tasks

- **Weekly**: Check disk usage and logs
- **Monthly**: Review database statistics and optimize queries
- **Quarterly**: Update Docker images and dependencies
- **Annually**: Review security policies and SSL certificates

### Backup Strategy

- Daily incremental backups
- Weekly full backups
- Monthly archive backups to cloud storage
- Test recovery procedures quarterly

---

**Document Version**: 1.0.0
**Last Updated**: 2026-04-11
