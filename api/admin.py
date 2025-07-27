from django.contrib import admin
from .models import Notification, Task


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'subject', 'is_sent', 'sent_at']
    list_filter = ['is_sent', 'sent_at']
    search_fields = ['email', 'subject', 'message']
    readonly_fields = ['sent_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'completed_at'] 