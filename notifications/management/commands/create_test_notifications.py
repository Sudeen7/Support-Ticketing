from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notifications.models import Notification
import random

class Command(BaseCommand):
    help = 'Creates test notifications for users'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username to create notifications for')
        parser.add_argument('--count', type=int, default=5, help='Number of notifications to create')

    def handle(self, *args, **options):
        username = options.get('user')
        count = options.get('count')

        if username:
            try:
                users = [User.objects.get(username=username)]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
                return
        else:
            users = User.objects.all()

        if not users:
            self.stdout.write(self.style.ERROR('No users found'))
            return

        titles = [
            'New ticket assigned',
            'Ticket status updated',
            'Comment added to your ticket',
            'Ticket priority changed',
            'System maintenance scheduled',
            'Your ticket was resolved',
            'Feedback requested',
            'Account settings updated',
            'Password change reminder',
            'New feature announcement'
        ]

        messages = [
            'A new ticket has been assigned to you.',
            'The status of your ticket has been updated.',
            'A new comment has been added to your ticket.',
            'The priority of your ticket has been changed.',
            'System maintenance is scheduled for tomorrow.',
            'Your ticket has been marked as resolved.',
            'Please provide feedback on your recent ticket.',
            'Your account settings have been updated.',
            'Remember to change your password regularly.',
            'We have added a new feature to the system.'
        ]

        notification_count = 0
        for user in users:
            for i in range(count):
                idx = random.randint(0, len(titles) - 1)
                read = random.choice([True, False])
                link = '/tickets/1/' if random.choice([True, False]) else None
                
                Notification.objects.create(
                    user=user,
                    title=titles[idx],
                    message=messages[idx],
                    read=read,
                    link=link
                )
                notification_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {notification_count} test notifications')
        )