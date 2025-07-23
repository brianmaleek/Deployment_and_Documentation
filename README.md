# Django Deployment with Celery and Swagger Documentation

A complete Django application with Celery background tasks, RabbitMQ message broker, and comprehensive Swagger API documentation. This project demonstrates best practices for deploying Django applications with asynchronous task processing.

## Features

- **Django REST Framework API** with comprehensive endpoints
- **Celery Background Tasks** for email notifications and data processing
- **RabbitMQ Message Broker** for reliable task queuing
- **Swagger/OpenAPI Documentation** accessible at `/swagger/`
- **Email Notification System** with SMTP integration
- **PostgreSQL Database** support for production
- **Docker & Docker Compose** for easy deployment
- **Multiple Deployment Options** (Heroku, AWS, DigitalOcean, PythonAnywhere)

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Deployment_and_Documentation
   ```

2. **Run with Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Django Admin: http://localhost:8000/admin/
   - Swagger Documentation: http://localhost:8000/swagger/
   - API Endpoints: http://localhost:8000/api/
   - RabbitMQ Management: http://localhost:15672/ (guest/guest)

### Manual Setup

1. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. **Setup database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Start services**
   ```bash
   # Terminal 1: Start RabbitMQ
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   
   # Terminal 2: Start Celery worker
   celery -A deployment_project worker --loglevel=info
   
   # Terminal 3: Start Celery beat
   celery -A deployment_project beat --loglevel=info
   
   # Terminal 4: Start Django
   python manage.py runserver
   ```

## API Endpoints

### Core Endpoints

- `GET /api/health/` - Health check
- `GET /api/celery-status/` - Celery worker status
- `POST /api/send-email/` - Send email notification

### User Management

- `GET /api/users/` - List all users
- `GET /api/users/{id}/` - Get user details

### Notifications

- `GET /api/notifications/` - List all notifications
- `POST /api/notifications/` - Create new notification
- `GET /api/notifications/{id}/` - Get notification details
- `GET /api/notifications/by_user/?user_id={id}` - Get notifications by user

### Background Tasks

- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new background task
- `GET /api/tasks/{id}/` - Get task details
- `GET /api/tasks/by_status/?status={status}` - Get tasks by status

## Swagger Documentation

Access the interactive API documentation at:
- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`
- **JSON Schema**: `/swagger.json`

## Deployment

### Quick Deployment Options

1. **Heroku** - [Deployment Guide](deployment_guide.md#option-1-heroku-deployment)
2. **DigitalOcean App Platform** - [Deployment Guide](deployment_guide.md#option-2-digitalocean-app-platform)
3. **AWS EC2** - [Deployment Guide](deployment_guide.md#option-3-aws-ec2-deployment)
4. **PythonAnywhere** - [Deployment Guide](deployment_guide.md#option-4-pythonanywhere-recommended-for-beginners)

### Environment Variables

Required environment variables for production:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DB_NAME=deployment_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=django-db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Testing

### Test Email Notifications

```bash
curl -X POST http://localhost:8000/api/send-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test Email",
    "message": "This is a test email from the application"
  }'
```

### Test Background Tasks

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Task",
    "description": "This is a test background task"
  }'
```

## Project Structure

```
Deployment_and_Documentation/
├── deployment_project/          # Django project settings
│   ├── settings.py             # Main settings file
│   ├── urls.py                 # URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   ├── asgi.py                 # ASGI configuration
│   └── celery.py               # Celery configuration
├── api/                        # API application
│   ├── models.py               # Database models
│   ├── views.py                # API views
│   ├── serializers.py          # DRF serializers
│   ├── tasks.py                # Celery tasks
│   ├── urls.py                 # API URLs
│   └── admin.py                # Admin interface
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Docker configuration
├── Procfile                    # Heroku deployment
├── env.example                 # Environment variables template
├── deployment_guide.md         # Comprehensive deployment guide
└── README.md                   # This file
```

## Celery Tasks

### Available Tasks

1. **send_email_notification(notification_id)** - Send email from notification record
2. **send_email_direct(to_email, subject, message, user_id)** - Send email directly
3. **process_background_task(task_id)** - Process background tasks
4. **periodic_health_check()** - Periodic health monitoring

### Task Monitoring

- **Celery Flower**: Monitor tasks in real-time
- **Django Admin**: View task results in admin interface
- **API Endpoints**: Check task status via API

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For deployment issues and questions:
1. Check the [Deployment Guide](deployment_guide.md)
2. Review the troubleshooting section
3. Check the logs and error messages
4. Open an issue on GitHub

## Acknowledgments

- Django REST Framework for the API framework
- Celery for background task processing
- RabbitMQ for message queuing
- drf-yasg for Swagger documentation
- Docker for containerization 