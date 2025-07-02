from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, FormView, UpdateView
from django.urls import reverse_lazy
from .models import UserProfile
from .serializers import UserSerializer, RegisterSerializer
from .permissions import IsAdmin
from .forms import UserRegistrationForm, UserProfileUpdateForm

# API Views
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

# Template Views
class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {username}!')
            return super().form_valid(form)
        return self.form_invalid(form)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        role = form.cleaned_data.get('role')
        profile = user.profile
        profile.role = role
        profile.save()
        messages.success(self.request, 'Your account has been created! You can now log in.')
        return super().form_valid(form)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Handle password update separately
        password = request.data.get('password')
        if password:
            instance.set_password(password)
            instance.save()
        
        self.perform_update(serializer)
        
        return Response(serializer.data)

class UserProfileAPIUpdateView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user.profile

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add ticket statistics based on user role
        if user.profile.role == 'client':
            from tickets.models import Ticket
            context['tickets_count'] = Ticket.objects.filter(created_by=user).count()
            context['open_tickets_count'] = Ticket.objects.filter(created_by=user, status__in=['open', 'in_progress', 'pending']).count()
            context['closed_tickets_count'] = Ticket.objects.filter(created_by=user, status__in=['resolved', 'closed']).count()
            context['recent_tickets'] = Ticket.objects.filter(created_by=user).order_by('-updated_at')[:5]
        
        elif user.profile.role == 'support':
            from tickets.models import Ticket
            context['assigned_tickets_count'] = Ticket.objects.filter(assigned_to=user).count()
            context['pending_tickets_count'] = Ticket.objects.filter(assigned_to=user, status__in=['open', 'in_progress', 'pending']).count()
            context['resolved_tickets_count'] = Ticket.objects.filter(assigned_to=user, status__in=['resolved', 'closed']).count()
            context['recent_tickets'] = Ticket.objects.filter(assigned_to=user).order_by('-updated_at')[:5]
        
        elif user.profile.role == 'admin':
            from tickets.models import Ticket
            from django.contrib.auth.models import User
            context['total_tickets_count'] = Ticket.objects.all().count()
            context['users_count'] = User.objects.all().count()
            context['unassigned_tickets_count'] = Ticket.objects.filter(assigned_to=None).count()
            context['closed_tickets_count'] = Ticket.objects.filter(status__in=['resolved', 'closed']).count()
            context['recent_tickets'] = Ticket.objects.all().order_by('-updated_at')[:5]
        
        return context

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileUpdateForm
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully.')
        return response
