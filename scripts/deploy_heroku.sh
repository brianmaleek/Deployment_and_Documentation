#!/bin/bash

# Heroku Deployment Script
echo "🚀 Starting Heroku deployment..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run 'heroku login' first."
    exit 1
fi

# Get app name from user
read -p "Enter your Heroku app name: " APP_NAME

# Create app if it doesn't exist
if ! heroku apps:info --app $APP_NAME &> /dev/null; then
    echo "📦 Creating new Heroku app: $APP_NAME"
    heroku create $APP_NAME
else
    echo "✅ App $APP_NAME already exists"
fi

# Add PostgreSQL add-on
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:hobby-dev --app $APP_NAME

# Add Redis add-on for Celery
echo "🔴 Adding Redis for Celery..."
heroku addons:create heroku-redis:hobby-dev --app $APP_NAME

# Configure environment variables
echo "⚙️ Configuring environment variables..."
heroku config:set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" --app $APP_NAME
heroku config:set DEBUG=False --app $APP_NAME
heroku config:set ALLOWED_HOSTS="$APP_NAME.herokuapp.com" --app $APP_NAME

# Get email credentials
read -p "Enter your email address: " EMAIL_USER
read -s -p "Enter your email app password: " EMAIL_PASS
echo

heroku config:set EMAIL_HOST_USER="$EMAIL_USER" --app $APP_NAME
heroku config:set EMAIL_HOST_PASSWORD="$EMAIL_PASS" --app $APP_NAME

# Set Celery configuration
REDIS_URL=$(heroku config:get REDIS_URL --app $APP_NAME)
heroku config:set CELERY_BROKER_URL="$REDIS_URL" --app $APP_NAME
heroku config:set CELERY_RESULT_BACKEND="$REDIS_URL" --app $APP_NAME

# Deploy the application
echo "📤 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Run migrations
echo "🗃️ Running database migrations..."
heroku run python manage.py migrate --app $APP_NAME

# Create superuser
echo "👤 Creating superuser..."
heroku run python manage.py createsuperuser --app $APP_NAME

# Scale workers
echo "⚡ Scaling Celery workers..."
heroku ps:scale worker=1 --app $APP_NAME

echo "✅ Deployment completed!"
echo "🌐 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📚 Swagger documentation: https://$APP_NAME.herokuapp.com/swagger/"
echo "🔧 Admin interface: https://$APP_NAME.herokuapp.com/admin/" 