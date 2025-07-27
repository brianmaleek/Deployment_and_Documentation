from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send-email/', views.send_email, name='send-email'),
    path('health/', views.health_check, name='health-check'),
    path('celery-status/', views.celery_status, name='celery-status'),
] 