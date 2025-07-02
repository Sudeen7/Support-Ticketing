from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_ticket_creation_notification(ticket):
    """
    Send email notification when a new ticket is created
    """
    subject = f'New Ticket Created: {ticket.title}'
    message = f'''
    A new ticket has been created:
    
    Title: {ticket.title}
    Description: {ticket.description}
    Priority: {ticket.get_priority_display()}
    Category: {ticket.category.name if ticket.category else 'Not specified'}
    Department: {ticket.department.name if ticket.department else 'Not specified'}
    Created by: {ticket.created_by.username}
    '''
    
    # Get admin users who have email notifications enabled
    from django.contrib.auth.models import User
    from .models import NotificationPreference
    
    admins = User.objects.filter(
        profile__role='admin',
        notification_preferences__email_notifications=True
    )
    
    # Create recipient list
    recipient_list = []
    
    # Add admins to recipient list
    for admin in admins:
        if admin.email:
            recipient_list.append(admin.email)
    
    # Add assigned user if they have email notifications enabled
    if ticket.assigned_to and ticket.assigned_to.email:
        try:
            if ticket.assigned_to.notification_preferences.email_notifications:
                recipient_list.append(ticket.assigned_to.email)
        except NotificationPreference.DoesNotExist:
            pass
    
    # Only send if there are recipients
    if recipient_list:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

def send_ticket_update_notification(ticket, previous_status):
    """
    Send email notification when a ticket's status is updated
    """
    subject = f'Ticket Status Updated: {ticket.title}'
    message = f'''
    A ticket's status has been updated:
    
    Title: {ticket.title}
    Previous Status: {previous_status}
    New Status: {ticket.get_status_display()}
    Priority: {ticket.get_priority_display()}
    Category: {ticket.category.name if ticket.category else 'Not specified'}
    Department: {ticket.department.name if ticket.department else 'Not specified'}
    '''
    
    from .models import NotificationPreference
    
    # Create recipient list
    recipient_list = []
    
    # Add ticket creator if they have email notifications enabled
    if ticket.created_by and ticket.created_by.email:
        try:
            if ticket.created_by.notification_preferences.email_notifications:
                recipient_list.append(ticket.created_by.email)
        except NotificationPreference.DoesNotExist:
            pass
    
    # Add assigned user if they have email notifications enabled
    if ticket.assigned_to and ticket.assigned_to.email:
        try:
            if ticket.assigned_to.notification_preferences.email_notifications:
                recipient_list.append(ticket.assigned_to.email)
        except NotificationPreference.DoesNotExist:
            pass
    
    # Only send if there are recipients
    if recipient_list:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )

def send_comment_notification(comment):
    """
    Send email notification when a new comment is added to a ticket
    """
    ticket = comment.ticket
    subject = f'New Comment on Ticket: {ticket.title}'
    
    # Get the absolute URL for the ticket detail page
    ticket_url = f"{settings.BASE_URL if hasattr(settings, 'BASE_URL') else ''}" + reverse('ticket_detail', kwargs={'pk': ticket.pk})
    
    message = f'''
    A new comment has been added to a ticket:
    
    Ticket: {ticket.title}
    Comment by: {comment.author.username}
    Comment: {comment.text}
    
    View the ticket at: {ticket_url}
    '''
    
    from .models import NotificationPreference
    
    # Create recipient list
    recipient_list = []
    
    # Add ticket creator if they have email notifications enabled and didn't make the comment
    if ticket.created_by and ticket.created_by.email and ticket.created_by != comment.author:
        try:
            if ticket.created_by.notification_preferences.email_notifications:
                recipient_list.append(ticket.created_by.email)
        except NotificationPreference.DoesNotExist:
            pass
    
    # Add assigned user if they have email notifications enabled and didn't make the comment
    if ticket.assigned_to and ticket.assigned_to.email and ticket.assigned_to != comment.author:
        try:
            if ticket.assigned_to.notification_preferences.email_notifications:
                recipient_list.append(ticket.assigned_to.email)
        except NotificationPreference.DoesNotExist:
            pass
    
    # Only send if there are recipients
    if recipient_list:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
