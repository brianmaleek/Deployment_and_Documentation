from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """Model for storing email notifications"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Notification to {self.email}: {self.subject}"


class Task(models.Model):
    """Model for storing background tasks"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    result = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.status}" 