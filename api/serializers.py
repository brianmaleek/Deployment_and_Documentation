from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notification, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['sent_at', 'is_sent', 'error_message']


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['subject', 'message', 'email']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'completed_at', 'status', 'result']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['name', 'description']


class EmailNotificationSerializer(serializers.Serializer):
    """Serializer for email notification requests"""
    to_email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    user_id = serializers.IntegerField(required=False) 