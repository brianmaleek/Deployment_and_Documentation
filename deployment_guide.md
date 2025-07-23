# Django Deployment Guide with Celery and Swagger

This guide provides step-by-step instructions for deploying the Django application with Celery and RabbitMQ to various cloud platforms.

## Prerequisites

- Python 3.11+
- Git
- A cloud platform account (Heroku, AWS, DigitalOcean, etc.)
- Email service credentials (Gmail, SendGrid, etc.)

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd Deployment_and_Documentation
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
SECRET_KEY=your-actual-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run with Docker (Recommended)

```bash
docker-compose up --build
```

This will start:
- Django web server on http://localhost:8000
- Celery worker
- Celery beat scheduler
- PostgreSQL database
- RabbitMQ message broker
- RabbitMQ management interface on http://localhost:15672

### 5. Run Locally (Alternative)

Start RabbitMQ:
```bash
# Install RabbitMQ or use Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

Start Celery worker:
```bash
celery -A deployment_project worker --loglevel=info
```

Start Celery beat (in another terminal):
```bash
celery -A deployment_project beat --loglevel=info
```

Start Django:
```bash
python manage.py runserver
```

## Deployment Options

### Option 1: Heroku Deployment

#### 1. Install Heroku CLI and Login

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

#### 2. Create Heroku App

```bash
heroku create your-app-name
```

#### 3. Add PostgreSQL Add-on

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

#### 4. Add Redis Add-on (for Celery)

```bash
heroku addons:create heroku-redis:hobby-dev
```

#### 5. Configure Environment Variables

```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
heroku config:set CELERY_BROKER_URL="$(heroku config:get REDIS_URL)"
heroku config:set CELERY_RESULT_BACKEND="$(heroku config:get REDIS_URL)"
```

#### 6. Deploy

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### 7. Run Migrations

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### 8. Scale Workers

```bash
heroku ps:scale worker=1
```

### Option 2: DigitalOcean App Platform

#### 1. Create App

1. Go to DigitalOcean App Platform
2. Connect your GitHub repository
3. Select the repository

#### 2. Configure Services

**Web Service:**
- Source: `/`
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- Run Command: `gunicorn deployment_project.wsgi:application --bind 0.0.0.0:$PORT`

**Worker Service:**
- Source: `/`
- Build Command: `pip install -r requirements.txt`
- Run Command: `celery -A deployment_project worker --loglevel=info`

#### 3. Environment Variables

Add these environment variables:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `CELERY_BROKER_URL` (Redis URL)
- `CELERY_RESULT_BACKEND` (Redis URL)

#### 4. Database

Add a PostgreSQL database and configure the connection.

### Option 3: AWS EC2 Deployment

#### 1. Launch EC2 Instance

1. Launch Ubuntu 22.04 LTS instance
2. Configure security groups for ports 22, 80, 443, 8000

#### 2. Connect and Setup

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Install Node.js (for npm)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 3. Setup PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE deployment_db;
CREATE USER deployment_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE deployment_db TO deployment_user;
\q
```

#### 4. Setup Redis

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### 5. Deploy Application

```bash
# Clone repository
git clone <your-repo-url>
cd Deployment_and_Documentation

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your values

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 6. Setup Gunicorn

```bash
# Create gunicorn service
sudo nano /etc/systemd/system/gunicorn.service
```

Add:
```ini
[Unit]
Description=Gunicorn daemon for Django deployment
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Deployment_and_Documentation
ExecStart=/home/ubuntu/Deployment_and_Documentation/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/Deployment_and_Documentation/deployment_project.sock deployment_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 7. Setup Celery

```bash
# Create celery service
sudo nano /etc/systemd/system/celery.service
```

Add:
```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=ubuntu
Group=www-data
EnvironmentFile=/home/ubuntu/Deployment_and_Documentation/.env
WorkingDirectory=/home/ubuntu/Deployment_and_Documentation
ExecStart=/bin/sh -c '${WorkingDirectory}/venv/bin/celery multi start worker1 -A deployment_project -l info'
ExecStop=/bin/sh -c '${WorkingDirectory}/venv/bin/celery multi stopwait worker1 -A deployment_project'
ExecReload=/bin/sh -c '${WorkingDirectory}/venv/bin/celery multi restart worker1 -A deployment_project -l info'

[Install]
WantedBy=multi-user.target
```

#### 8. Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/deployment_project
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/Deployment_and_Documentation;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/Deployment_and_Documentation/deployment_project.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/deployment_project /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. Start Services

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl start celery
sudo systemctl enable celery
```

### Option 4: PythonAnywhere (Recommended for Beginners)

#### 1. Create Account

1. Go to [PythonAnywhere](https://www.pythonanywhere.com)
2. Create a free account

#### 2. Upload Code

1. Go to Files tab
2. Upload your project files or clone from Git

#### 3. Setup Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.11 deployment_env
pip install -r requirements.txt
```

#### 4. Configure WSGI

Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py`:

```python
import os
import sys

path = '/home/yourusername/Deployment_and_Documentation'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'deployment_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 5. Setup Database

Use PythonAnywhere's built-in SQLite or MySQL.

#### 6. Configure Environment

Create `.env` file in your project directory with your settings.

#### 7. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

## Testing the Deployment

### 1. Test API Endpoints

Visit your deployed URL and test these endpoints:

- **Swagger Documentation**: `https://your-domain.com/swagger/`
- **Health Check**: `https://your-domain.com/api/health/`
- **Celery Status**: `https://your-domain.com/api/celery-status/`

### 2. Test Email Notifications

Send a POST request to `/api/send-email/`:

```json
{
    "to_email": "test@example.com",
    "subject": "Test Email",
    "message": "This is a test email from the deployed application"
}
```

### 3. Test Background Tasks

Create a new task via the API and verify it's processed by Celery.

## Troubleshooting

### Common Issues

1. **Celery Worker Not Starting**
   - Check RabbitMQ/Redis connection
   - Verify environment variables
   - Check logs: `celery -A deployment_project worker --loglevel=debug`

2. **Email Not Sending**
   - Verify email credentials
   - Check SMTP settings
   - Ensure Celery worker is running

3. **Database Connection Issues**
   - Verify database credentials
   - Check database server status
   - Ensure migrations are applied

4. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check static files configuration
   - Verify web server configuration

### Logs and Monitoring

- **Django Logs**: Check application logs
- **Celery Logs**: Monitor worker logs
- **System Logs**: Check system service logs
- **Nginx Logs**: `/var/log/nginx/error.log`

## Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **HTTPS**: Use SSL certificates in production
3. **Firewall**: Configure proper firewall rules
4. **Updates**: Keep dependencies updated
5. **Backups**: Regular database backups

## Performance Optimization

1. **Caching**: Implement Redis caching
2. **CDN**: Use CDN for static files
3. **Database**: Optimize database queries
4. **Monitoring**: Use monitoring tools (New Relic, Sentry)

## Support

For issues and questions:
1. Check the logs
2. Review this documentation
3. Search for similar issues online
4. Contact your deployment platform support 