from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from tickets.models import Ticket, Comment
from .models import Notification
from .email_utils import send_ticket_creation_notification, send_ticket_update_notification, send_comment_notification

@receiver(post_save, sender=Ticket)
def ticket_created_notification(sender, instance, created, **kwargs):
    """
    Send notification when a new ticket is created
    """
    if created:
        # Send email notification
        send_ticket_creation_notification(instance)
        
        # Create in-app notification for admin users
        from django.contrib.auth.models import User
        admins = User.objects.filter(profile__role='admin')
        ticket_url = reverse('ticket_detail', kwargs={'pk': instance.pk})
        
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title='New Ticket Created',
                message=f'A new ticket "{instance.title}" has been created by {instance.created_by.username}.',
                link=ticket_url
            )
        
        # If assigned to someone, notify them too
        if instance.assigned_to:
            Notification.objects.create(
                user=instance.assigned_to,
                title='Ticket Assigned to You',
                message=f'Ticket "{instance.title}" has been assigned to you.',
                link=ticket_url
            )

@receiver(pre_save, sender=Ticket)
def ticket_status_changed_notification(sender, instance, **kwargs):
    """
    Send notification when a ticket's status is changed
    """
    # Check if this is an existing ticket (not a new one)
    if instance.pk:
        try:
            # Get the previous state of the ticket
            old_instance = Ticket.objects.get(pk=instance.pk)
            
            # If status has changed, send notification
            if old_instance.status != instance.status:
                # Send email notification
                send_ticket_update_notification(instance, old_instance.get_status_display())
                
                # Create in-app notification for the ticket creator
                ticket_url = reverse('ticket_detail', kwargs={'pk': instance.pk})
                
                # Notify the ticket creator
                Notification.objects.create(
                    user=instance.created_by,
                    title='Ticket Status Updated',
                    message=f'Your ticket "{instance.title}" status has been changed from {old_instance.get_status_display()} to {instance.get_status_display()}.',
                    link=ticket_url
                )
                
                # If assigned to someone and they didn't make the change, notify them too
                if instance.assigned_to and instance.assigned_to != instance.updated_by:
                    Notification.objects.create(
                        user=instance.assigned_to,
                        title='Ticket Status Updated',
                        message=f'Ticket "{instance.title}" status has been changed from {old_instance.get_status_display()} to {instance.get_status_display()}.',
                        link=ticket_url
                    )
        except Ticket.DoesNotExist:
            pass  # This shouldn't happen, but just in case

@receiver(post_save, sender=Comment)
def comment_created_notification(sender, instance, created, **kwargs):
    if created:
        ticket = instance.ticket
        ticket_url = reverse('ticket_detail', kwargs={'pk': ticket.pk})
        
        # Notify the ticket creator if they didn't make the comment
        if ticket.created_by != instance.author:
            Notification.objects.create(
                user=ticket.created_by,
                title='New Comment on Your Ticket',
                message=f'A new comment has been added to your ticket "{ticket.title}" by {instance.author.username}.',
                link=ticket_url
            )
        
        # Notify the assigned support staff if they didn't make the comment
        if ticket.assigned_to and ticket.assigned_to != instance.author:
            Notification.objects.create(
                user=ticket.assigned_to,
                title='New Comment on Assigned Ticket',
                message=f'A new comment has been added to ticket "{ticket.title}" by {instance.author.username}.',
                link=ticket_url
            )
        
        # Notify admins who didn't make the comment
        from django.contrib.auth.models import User
        admins = User.objects.filter(profile__role='admin').exclude(id=instance.author.id)
        
        for admin in admins:
            Notification.objects.create(
                user=admin,
                title='New Comment on Ticket',
                message=f'A new comment has been added to ticket "{ticket.title}" by {instance.author.username}.',
                link=ticket_url
            )
        
        # Send email notifications
        send_comment_notification(instance)
