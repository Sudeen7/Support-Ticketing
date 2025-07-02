from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from .forms import NotificationPreferencesForm
from .models import NotificationPreference, Notification

@method_decorator(login_required, name='dispatch')
class NotificationPreferencesView(UpdateView):
    model = NotificationPreference
    form_class = NotificationPreferencesForm
    template_name = 'notifications/preferences.html'
    success_url = reverse_lazy('notification_preferences')
    
    def get_object(self, queryset=None):
        # Get or create notification preferences for the current user
        obj, created = NotificationPreference.objects.get_or_create(user=self.request.user)
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, "Notification preferences updated successfully.")
        return super().form_valid(form)

@login_required
def notification_list(request):
    # Get user's notifications
    notifications = request.user.notifications.all().order_by('-created_at')
    
    # Mark all as read if requested
    if 'mark_all_read' in request.GET:
        notifications.update(read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('notification_list')
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request):
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        all_notifications = request.POST.get('all', 'false') == 'true'
        
        if all_notifications:
            # Mark all notifications as read
            request.user.notifications.all().update(read=True)
            return JsonResponse({'status': 'success', 'message': 'All notifications marked as read'})
        elif notification_id:
            # Mark specific notification as read
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
