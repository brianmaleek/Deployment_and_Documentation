from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Notification, Task
from .serializers import (
    UserSerializer, NotificationSerializer, NotificationCreateSerializer,
    TaskSerializer, TaskCreateSerializer, EmailNotificationSerializer
)
from .tasks import send_email_notification, send_email_direct, process_background_task


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user instances.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        notification = serializer.save()
        # Trigger Celery task to send email
        send_email_notification.delay(notification.id)

    @swagger_auto_schema(
        operation_description="Get notifications by user ID",
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get notifications for a specific user"""
        user_id = request.query_params.get('user_id')
        if user_id:
            notifications = self.queryset.filter(user_id=user_id)
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        return Response({'error': 'user_id parameter required'}, status=400)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing background tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save()
        # Trigger Celery task to process background task
        process_background_task.delay(task.id)

    @swagger_auto_schema(
        operation_description="Get tasks by status",
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get tasks by status"""
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = self.queryset.filter(status=status_filter)
            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data)
        return Response({'error': 'status parameter required'}, status=400)


@swagger_auto_schema(
    method='post',
    request_body=EmailNotificationSerializer,
    operation_description="Send an email notification immediately",
    responses={
        200: openapi.Response(
            description="Email sent successfully",
            examples={
                "application/json": {
                    "message": "Email sent successfully",
                    "task_id": "task-uuid-here"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "error": "Invalid email data"
                }
            }
        )
    }
)
@api_view(['POST'])
def send_email(request):
    """
    Send an email notification immediately using Celery
    """
    serializer = EmailNotificationSerializer(data=request.data)
    if serializer.is_valid():
        # Trigger Celery task
        task = send_email_direct.delay(
            to_email=serializer.validated_data['to_email'],
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message'],
            user_id=serializer.validated_data.get('user_id')
        )
        
        return Response({
            'message': 'Email sent successfully',
            'task_id': task.id
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Get API health status",
    responses={
        200: openapi.Response(
            description="API is healthy",
            examples={
                "application/json": {
                    "status": "healthy",
                    "message": "API is running"
                }
            }
        )
    }
)
@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'message': 'API is running'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get Celery worker status",
    responses={
        200: openapi.Response(
            description="Celery worker status",
            examples={
                "application/json": {
                    "celery_status": "running",
                    "message": "Celery worker is active"
                }
            }
        )
    }
)
@api_view(['GET'])
def celery_status(request):
    """
    Check Celery worker status
    """
    try:
        from celery.result import AsyncResult
        # Try to get a simple task result to check if Celery is working
        result = AsyncResult("test-task-id")
        return Response({
            'celery_status': 'running',
            'message': 'Celery worker is active'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'celery_status': 'error',
            'message': f'Celery worker error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 