import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import Notification, Task
from datetime import datetime

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(notification_id):
    """
    Celery task to send email notifications
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Update task status to running
        notification.is_sent = False
        notification.save()
        
        # Send email
        send_mail(
            subject=notification.subject,
            message=notification.message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[notification.email],
            fail_silently=False,
        )
        
        # Update notification as sent
        notification.is_sent = True
        notification.save()
        
        logger.info(f"Email sent successfully to {notification.email}")
        return f"Email sent to {notification.email}"
        
    except Notification.DoesNotExist:
        logger.error(f"Notification with id {notification_id} not found")
        return "Notification not found"
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        # Update notification with error
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.error_message = str(e)
            notification.save()
        except:
            pass
        return f"Error sending email: {str(e)}"


@shared_task
def send_email_direct(to_email, subject, message, user_id=None):
    """
    Direct email sending task
    """
    try:
        # Create notification record
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        notification = Notification.objects.create(
            user=user,
            subject=subject,
            message=message,
            email=to_email,
        )
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            fail_silently=False,
        )
        
        # Update notification as sent
        notification.is_sent = True
        notification.save()
        
        logger.info(f"Direct email sent successfully to {to_email}")
        return f"Email sent to {to_email}"
        
    except Exception as e:
        logger.error(f"Error sending direct email: {str(e)}")
        return f"Error sending email: {str(e)}"


@shared_task
def process_background_task(task_id):
    """
    Process a background task
    """
    try:
        task = Task.objects.get(id=task_id)
        task.status = 'running'
        task.save()
        
        # Simulate some background processing
        import time
        time.sleep(5)  # Simulate work
        
        # Update task as completed
        task.status = 'completed'
        task.completed_at = datetime.now()
        task.result = f"Task {task.name} completed successfully"
        task.save()
        
        logger.info(f"Background task {task.name} completed")
        return f"Task {task.name} completed"
        
    except Task.DoesNotExist:
        logger.error(f"Task with id {task_id} not found")
        return "Task not found"
    except Exception as e:
        logger.error(f"Error processing task: {str(e)}")
        try:
            task = Task.objects.get(id=task_id)
            task.status = 'failed'
            task.result = str(e)
            task.save()
        except:
            pass
        return f"Error processing task: {str(e)}"


@shared_task
def periodic_health_check():
    """
    Periodic health check task
    """
    logger.info("Health check task running")
    return "Health check completed" 