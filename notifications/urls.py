from django.urls import path
from .views import NotificationPreferencesView, notification_list, mark_notification_read

urlpatterns = [
    path('list/', notification_list, name='notification_list'),
    path('preferences/', NotificationPreferencesView.as_view(), name='notification_preferences'),
    path('mark-read/', mark_notification_read, name='mark_notification_read'),
]