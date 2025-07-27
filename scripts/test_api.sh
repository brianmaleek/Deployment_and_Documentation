#!/bin/bash

# API Testing Script
BASE_URL=${1:-"http://localhost:8000"}

echo "🧪 Testing API endpoints at $BASE_URL"
echo "======================================"

# Test health check
echo "1. Testing health check..."
curl -s "$BASE_URL/api/health/" | jq . || echo "Health check failed"

# Test Celery status
echo -e "\n2. Testing Celery status..."
curl -s "$BASE_URL/api/celery-status/" | jq . || echo "Celery status check failed"

# Test email notification
echo -e "\n3. Testing email notification..."
curl -s -X POST "$BASE_URL/api/send-email/" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "test@example.com",
    "subject": "Test Email from API",
    "message": "This is a test email sent via the API"
  }' | jq . || echo "Email test failed"

# Test creating a background task
echo -e "\n4. Testing background task creation..."
curl -s -X POST "$BASE_URL/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Background Task",
    "description": "This is a test background task created via API"
  }' | jq . || echo "Task creation failed"

# Test getting users
echo -e "\n5. Testing users endpoint..."
curl -s "$BASE_URL/api/users/" | jq . || echo "Users endpoint failed"

# Test getting notifications
echo -e "\n6. Testing notifications endpoint..."
curl -s "$BASE_URL/api/notifications/" | jq . || echo "Notifications endpoint failed"

# Test getting tasks
echo -e "\n7. Testing tasks endpoint..."
curl -s "$BASE_URL/api/tasks/" | jq . || echo "Tasks endpoint failed"

echo -e "\n✅ API testing completed!"
echo "📚 Swagger documentation: $BASE_URL/swagger/" 