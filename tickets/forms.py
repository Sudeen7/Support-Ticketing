from django import forms
from .models import Ticket, Comment, Category, Department
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())
    department = forms.ModelChoiceField(queryset=Department.objects.all())

    
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'department', 'priority', 'status', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'})

        
        # Make assigned_to field show only support users
        self.fields['assigned_to'].queryset = User.objects.filter(profile__role='support')
        self.fields['assigned_to'].required = False
        
        # Set initial values for category and department if editing an existing ticket
        if self.instance and self.instance.pk:
            if self.instance.category:
                self.fields['category'].initial = self.instance.category.code
            if self.instance.department:
                self.fields['department'].initial = self.instance.department.code
        
        # Customize fields based on user role
        if user and user.profile.role == 'client':
            # Clients can't set status or assigned_to
            if 'status' in self.fields:
                self.fields.pop('status')
            if 'assigned_to' in self.fields:
                self.fields.pop('assigned_to')
        elif user and user.profile.role == 'support':
            # Support can set status but not assigned_to
            if 'assigned_to' in self.fields:
                self.fields.pop('assigned_to')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment here...'}),
        }
        labels = {
            'text': '',
        }

class TicketFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Status')] + list(Ticket.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All Priorities')] + list(Ticket.PRIORITY_CHOICES)
    CATEGORY_CHOICES = [('', 'All Categories')] + list(Category.CATEGORY_CHOICES)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search tickets...'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class TicketAssignForm(forms.Form):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='support'),
        required=True,
        empty_label="Select Support Staff"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].widget.attrs.update({'class': 'form-control'})

class TicketStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=Ticket.STATUS_CHOICES, required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-control'})