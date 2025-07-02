from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    DEPARTMENT_CHOICES = [ 
        ('tech_support', 'Technical Support'), 
        ('customer_service', 'Customer Service'), 
        ('billing', 'Billing & Accounts'), 
        ('product_support', 'Product Support'), 
        ('sales', 'Sales & Marketing'), 
        ('security', 'Security & Compliance'), 
        ('admin', 'Administration'), 
        ('other', 'Other'), 
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='other', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    CATEGORY_CHOICES = [ 
        ('technical', 'Technical Issues'), 
        ('account', 'Account Issues'), 
        ('billing', 'Billing and Payments'), 
        ('product', 'Product/Service Support'), 
        ('feedback', 'Feedback and Suggestions'), 
        ('security', 'Security Concerns'), 
        ('other', 'Other'), 
    ]
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('reopened', 'Reopened'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='tickets')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='tickets')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.title}"
