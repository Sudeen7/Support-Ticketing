from django import forms
from .models import NotificationPreference

class NotificationPreferencesForm(forms.ModelForm):
    email_notifications = forms.BooleanField(required=False, initial=True,
                                           help_text="Receive email notifications for ticket updates")
    
    class Meta:
        model = NotificationPreference
        fields = ['email_notifications']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value from the instance
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['email_notifications'].initial = kwargs['instance'].email_notifications