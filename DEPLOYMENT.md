# Deployment Guide

This guide covers deploying the Smart Attendance System to production.

---

## Prerequisites

- Ubuntu 20.04+ (or similar Linux distribution)
- Python 3.8+
- Node.js 14+
- Nginx
- SSL certificate (Let's Encrypt recommended)
- Domain name (optional but recommended)

---

## Backend Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3-pip python3-venv python3-dev -y
sudo apt install build-essential cmake -y
sudo apt install libopencv-dev python3-opencv -y

# Install PostgreSQL (optional, for production database)
sudo apt install postgresql postgresql-contrib -y
```

### 2. Clone Repository

```bash
cd /var/www
sudo git clone <your-repo-url> smart-attendance
sudo chown -R $USER:$USER smart-attendance
cd smart-attendance
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install production server
pip install gunicorn

# Create directories
mkdir -p models dataset logs

# Copy and configure environment
cp .env.example .env
nano .env  # Edit configuration
```

### 4. Configure Environment (.env)

```env
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_PATH=/var/www/smart-attendance/backend/attendance.db

# Security
SECRET_KEY=<generate-strong-secret-key>
CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=WARNING
```

### 5. Create Systemd Service

Create `/etc/systemd/system/smart-attendance.service`:

```ini
[Unit]
Description=Smart Attendance System Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/smart-attendance/backend
Environment="PATH=/var/www/smart-attendance/backend/venv/bin"
ExecStart=/var/www/smart-attendance/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /var/www/smart-attendance/backend/logs/access.log \
    --error-logfile /var/www/smart-attendance/backend/logs/error.log

[Install]
WantedBy=multi-user.target
```

### 6. Start Service

```bash
# Set permissions
sudo chown -R www-data:www-data /var/www/smart-attendance

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable smart-attendance
sudo systemctl start smart-attendance

# Check status
sudo systemctl status smart-attendance
```

---

## Frontend Deployment

### 1. Build Frontend

```bash
cd /var/www/smart-attendance/frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/smart-attendance`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for face recognition
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/smart-attendance/frontend/build;
    index index.html;

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Enable Site and SSL

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smart-attendance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Database Backup

### 1. Automated Backup Script

Create `/var/www/smart-attendance/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/smart-attendance"
DB_PATH="/var/www/smart-attendance/backend/attendance.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $DB_PATH $BACKUP_DIR/attendance_$DATE.db

# Backup face encodings
cp /var/www/smart-attendance/backend/models/face_encodings.pkl \
   $BACKUP_DIR/face_encodings_$DATE.pkl

# Keep only last 30 days
find $BACKUP_DIR -name "attendance_*.db" -mtime +30 -delete
find $BACKUP_DIR -name "face_encodings_*.pkl" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2. Schedule Backup

```bash
# Make executable
chmod +x /var/www/smart-attendance/backup.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
```

Add line:
```
0 2 * * * /var/www/smart-attendance/backup.sh >> /var/log/smart-attendance-backup.log 2>&1
```

---

## Security Hardening

### 1. Firewall

```bash
# Install UFW
sudo apt install ufw -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Fail2Ban

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Rate Limiting (Nginx)

Add to Nginx config:

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        # ... rest of config
    }
}
```

---

## Monitoring

### 1. Application Logs

```bash
# View backend logs
sudo journalctl -u smart-attendance -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. System Monitoring

Install monitoring tools:

```bash
# htop for system monitoring
sudo apt install htop -y

# Optional: Prometheus + Grafana for advanced monitoring
```

---

## Performance Optimization

### 1. Enable Caching

Add Redis for caching (optional):

```bash
# Install Redis
sudo apt install redis-server -y
sudo systemctl enable redis-server

# Configure Redis in application
pip install redis
```

### 2. Database Optimization

For production with many records, consider:

```bash
# Migrate to PostgreSQL
sudo -u postgres createdb smart_attendance
sudo -u postgres createuser attendance_user

# Update database connection in application
```

### 3. Image Optimization

```bash
# Install image optimization tools
sudo apt install jpegoptim optipng -y

# Optimize uploaded images in application
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or HAProxy
2. **Multiple App Instances**: Run multiple Gunicorn instances
3. **Shared Storage**: Use NFS or S3 for face encodings
4. **Database Replication**: PostgreSQL master-slave setup

### Vertical Scaling

1. **Increase Workers**: Adjust Gunicorn workers
2. **GPU Support**: Enable CUDA for faster face recognition
3. **Memory Caching**: Use Redis for session management

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u smart-attendance -n 50

# Check permissions
ls -la /var/www/smart-attendance/backend

# Check port
sudo netstat -tlnp | grep 8000
```

### High CPU Usage

```bash
# Monitor processes
htop

# Reduce Gunicorn workers
# Edit /etc/systemd/system/smart-attendance.service

# Restart service
sudo systemctl restart smart-attendance
```

### Database Locked

```bash
# Check database connections
sudo lsof | grep attendance.db

# Restart service
sudo systemctl restart smart-attendance
```

---

## Maintenance

### Update Application

```bash
cd /var/www/smart-attendance

# Pull latest code
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Rebuild frontend
cd ../frontend
npm install
npm run build

# Restart services
sudo systemctl restart smart-attendance
sudo systemctl restart nginx
```

### Database Migration

When database schema changes:

```bash
# Backup current database
cp attendance.db attendance.db.backup

# Apply migrations (implement migration script)
python scripts/migrate.py
```

---

## Support

For deployment issues:
- Check application logs
- Review Nginx error logs
- Verify environment configuration
- Ensure all dependencies are installed

---

**Remember**: Always test deployment procedures in a staging environment before applying to production!
