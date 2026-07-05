# Staging Deployment Guide 🚀

## Overview

This guide covers deploying the NBFC Financial Suite to a staging environment using Docker Compose, Nginx reverse proxy, and automated CI/CD with GitHub Actions.

---

## 📋 Prerequisites

### Server Requirements

- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: Minimum 4GB (8GB recommended)
- **CPU**: 2+ cores
- **Storage**: 50GB+ SSD
- **Network**: Public IP with ports 80, 443 accessible

### Software Requirements

- Docker 24.0+
- Docker Compose 2.0+
- Git
- (Optional) SSL certificates for HTTPS

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Internet/Users                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ Port 80/443
                        ▼
            ┌───────────────────────┐
            │   Nginx Reverse Proxy  │
            │   - Load Balancing     │
            │   - SSL Termination    │
            │   - Rate Limiting      │
            └───────┬───────────────┘
                    │
        ┌───────────┴──────────────┐
        │                          │
        ▼                          ▼
┌──────────────┐          ┌──────────────┐
│   Frontend   │          │   Backend    │
│  (Next.js)   │          │  (FastAPI)   │
│  Port 3000   │          │  Port 8000   │
└──────────────┘          └───────┬──────┘
                                  │
                      ┌───────────┴──────────┐
                      │                      │
                      ▼                      ▼
              ┌──────────────┐      ┌──────────────┐
              │  PostgreSQL  │      │    Redis     │
              │   Port 5432  │      │  Port 6379   │
              └──────────────┘      └──────────────┘
```

---

## 🚀 Deployment Steps

### 1. Server Setup

#### 1.1 Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### 1.2 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### 1.3 Install Git

```bash
sudo apt install git -y
git --version
```

### 2. Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/nbfc-suite
sudo chown $USER:$USER /opt/nbfc-suite

# Clone repository
cd /opt/nbfc-suite
git clone https://github.com/yourusername/nbfc-suite.git .

# Checkout staging branch
git checkout develop
```

### 3. Configure Environment

#### 3.1 Create Environment File

```bash
# Copy example environment file
cp .env.staging.example .env.staging

# Edit environment variables
nano .env.staging
```

#### 3.2 Update Required Variables

```env
# Database Credentials
DB_PASSWORD=your_secure_database_password_here

# Redis Password
REDIS_PASSWORD=your_secure_redis_password_here

# Secret Keys (generate using: openssl rand -hex 32)
SECRET_KEY=your_secret_key_minimum_32_characters
JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters

# Domain
CORS_ORIGINS=https://staging.yourdomain.com
NEXT_PUBLIC_API_URL=https://staging.yourdomain.com/api/v1

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com
```

### 4. SSL Configuration (Optional but Recommended)

#### 4.1 Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 4.2 Generate SSL Certificate

```bash
# Stop nginx if running
docker compose -f docker-compose.staging.yml stop nginx

# Generate certificate
sudo certbot certonly --standalone -d staging.yourdomain.com

# Certificate will be saved in /etc/letsencrypt/live/staging.yourdomain.com/
```

#### 4.3 Copy Certificates

```bash
# Create SSL directory
mkdir -p ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem
```

#### 4.4 Update Nginx Configuration

Uncomment SSL lines in `nginx/conf.d/default.conf`:

```nginx
listen 443 ssl http2;
listen [::]:443 ssl http2;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### 5. Deploy Application

#### 5.1 Build and Start Services

```bash
# Build images
docker-compose -f docker-compose.staging.yml build

# Start services
docker-compose -f docker-compose.staging.yml up -d

# Check status
docker-compose -f docker-compose.staging.yml ps
```

#### 5.2 Run Database Migrations

```bash
# Run Alembic migrations
docker-compose -f docker-compose.staging.yml exec backend alembic upgrade head
```

#### 5.3 Create Initial Admin User (Optional)

```bash
# Access backend container
docker-compose -f docker-compose.staging.yml exec backend bash

# Run Python script to create admin user
python -c "
from backend.services.auth.service import AuthService
from backend.shared.database.connection import get_db
import asyncio

async def create_admin():
    async for db in get_db():
        service = AuthService(db)
        await service.create_user(
            email='admin@yourdomain.com',
            username='admin',
            password='Admin@123',
            first_name='System',
            last_name='Administrator',
            is_superuser=True
        )
        print('Admin user created!')

asyncio.run(create_admin())
"
```

### 6. Verify Deployment

#### 6.1 Check Service Health

```bash
# Check all containers are running
docker-compose -f docker-compose.staging.yml ps

# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check nginx
curl http://localhost
```

#### 6.2 Check Logs

```bash
# View all logs
docker-compose -f docker-compose.staging.yml logs

# View specific service logs
docker-compose -f docker-compose.staging.yml logs backend
docker-compose -f docker-compose.staging.yml logs frontend
docker-compose -f docker-compose.staging.yml logs postgres

# Follow logs in real-time
docker-compose -f docker-compose.staging.yml logs -f
```

#### 6.3 Access Application

- **Frontend**: https://staging.yourdomain.com
- **API Docs**: https://staging.yourdomain.com/docs
- **ReDoc**: https://staging.yourdomain.com/redoc
- **Health Check**: https://staging.yourdomain.com/health

### 7. Configure Automated Backups

#### 7.1 Create Backup Script

```bash
# Create backup directory
mkdir -p /opt/backups/nbfc-suite

# Create backup script
cat > /opt/nbfc-suite/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups/nbfc-suite"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose -f /opt/nbfc-suite/docker-compose.staging.yml exec -T postgres pg_dump -U nbfc_user nbfc_staging | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

# Uploads backup
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" /opt/nbfc-suite/uploads

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x /opt/nbfc-suite/backup.sh
```

#### 7.2 Schedule Backups with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/nbfc-suite/backup.sh >> /var/log/nbfc-backup.log 2>&1
```

---

## 🔄 CI/CD with GitHub Actions

### 1. Configure GitHub Secrets

Go to GitHub Repository → Settings → Secrets and Variables → Actions

Add the following secrets:

- `STAGING_HOST`: Staging server IP/hostname
- `STAGING_USER`: SSH username
- `STAGING_SSH_KEY`: Private SSH key for deployment
- `STAGING_PORT`: SSH port (default: 22)
- `STAGING_API_URL`: API URL for frontend build
- `SLACK_WEBHOOK_URL`: (Optional) Slack webhook for notifications

### 2. Configure SSH Access

#### 2.1 Generate SSH Key Pair

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_deploy.pub user@staging-server
```

#### 2.2 Add Private Key to GitHub

```bash
# Display private key
cat ~/.ssh/github_deploy

# Copy the entire output and add to GitHub Secrets as STAGING_SSH_KEY
```

### 3. Trigger Deployment

```bash
# Push to develop branch
git push origin develop

# Or manually trigger from GitHub Actions UI
```

### 4. Monitor Deployment

- Go to GitHub → Actions tab
- View deployment progress
- Check logs for each step

---

## 🔧 Management Commands

### Start Services

```bash
docker-compose -f docker-compose.staging.yml up -d
```

### Stop Services

```bash
docker-compose -f docker-compose.staging.yml down
```

### Restart Services

```bash
docker-compose -f docker-compose.staging.yml restart
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.staging.yml logs -f

# Specific service
docker-compose -f docker-compose.staging.yml logs -f backend
```

### Update Application

```bash
# Pull latest code
git pull origin develop

# Rebuild and restart
docker-compose -f docker-compose.staging.yml up -d --build

# Run migrations
docker-compose -f docker-compose.staging.yml exec backend alembic upgrade head
```

### Scale Services

```bash
# Scale backend to 3 instances
docker-compose -f docker-compose.staging.yml up -d --scale backend=3
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose -f docker-compose.staging.yml exec postgres psql -U nbfc_user -d nbfc_staging

# Backup database
docker-compose -f docker-compose.staging.yml exec postgres pg_dump -U nbfc_user nbfc_staging > backup.sql

# Restore database
cat backup.sql | docker-compose -f docker-compose.staging.yml exec -T postgres psql -U nbfc_user -d nbfc_staging
```

### Redis Operations

```bash
# Access Redis CLI
docker-compose -f docker-compose.staging.yml exec redis redis-cli -a <REDIS_PASSWORD>

# Clear cache
docker-compose -f docker-compose.staging.yml exec redis redis-cli -a <REDIS_PASSWORD> FLUSHALL
```

---

## 📊 Monitoring

### 1. Check Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Specific service resources
docker-compose -f docker-compose.staging.yml exec backend ps aux
```

### 2. Application Metrics

```bash
# API health
curl https://staging.yourdomain.com/health

# Prometheus metrics (if configured)
curl https://staging.yourdomain.com/metrics
```

### 3. Log Monitoring

```bash
# Access logs
tail -f logs/nginx/access.log

# Error logs
tail -f logs/nginx/error.log

# Application logs
docker-compose -f docker-compose.staging.yml logs -f backend
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.staging.yml logs <service-name>

# Check container status
docker-compose -f docker-compose.staging.yml ps

# Restart specific service
docker-compose -f docker-compose.staging.yml restart <service-name>
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.staging.yml ps postgres

# Test connection
docker-compose -f docker-compose.staging.yml exec postgres psql -U nbfc_user -d nbfc_staging -c "SELECT 1;"

# Check environment variables
docker-compose -f docker-compose.staging.yml exec backend env | grep DB_
```

### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services to clear memory
docker-compose -f docker-compose.staging.yml restart
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/staging.yourdomain.com/privkey.pem ssl/key.pem

# Restart nginx
docker-compose -f docker-compose.staging.yml restart nginx
```

---

## 🔒 Security Best Practices

1. **Change Default Credentials**
   - Update all passwords in `.env.staging`
   - Use strong, unique passwords

2. **Enable Firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   ```

3. **Regular Updates**
   - Update Docker images weekly
   - Apply security patches
   - Review and update dependencies

4. **Backup Strategy**
   - Daily database backups
   - Weekly full system backups
   - Test restore procedures

5. **Monitoring and Alerts**
   - Set up monitoring (Prometheus, Grafana)
   - Configure alerts for downtime
   - Monitor resource usage

6. **Access Control**
   - Use SSH keys (disable password authentication)
   - Implement IP whitelisting
   - Regular security audits

---

## 📝 Maintenance Checklist

### Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor resource usage

### Weekly
- [ ] Update Docker images
- [ ] Review backup status
- [ ] Check disk space
- [ ] Security scan

### Monthly
- [ ] Update dependencies
- [ ] Review access logs
- [ ] Performance optimization
- [ ] Security audit

---

## 🎯 Next Steps

After staging deployment:

1. **Testing**
   - Run smoke tests
   - Perform UAT (User Acceptance Testing)
   - Load testing

2. **Documentation**
   - Update API documentation
   - Create user guides
   - Document deployment process

3. **Production Preparation**
   - Review production requirements
   - Plan production deployment
   - Prepare rollback strategy

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.staging.yml logs`
- Review documentation
- Contact: support@yourdomain.com

---

**Last Updated**: July 5, 2026
**Version**: 2.0.0
