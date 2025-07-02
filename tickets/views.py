from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from .models import Department, Category, Ticket, Comment
from .serializers import (
    DepartmentSerializer, CategorySerializer,
    TicketListSerializer, TicketDetailSerializer, CommentSerializer
)
from .forms import TicketForm, CommentForm, TicketFilterForm, TicketAssignForm, TicketStatusUpdateForm
from accounts.permissions import IsAdmin, IsAdminOrSupport
from .permissions import CanViewTicket, CanUpdateTicket, CanDeleteTicket, CanCommentOnTicket

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TicketListSerializer
        return TicketDetailSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            if self.action == 'retrieve':
                permission_classes = [permissions.IsAuthenticated, CanViewTicket]
            elif self.action in ['update', 'partial_update']:
                permission_classes = [permissions.IsAuthenticated, CanUpdateTicket]
            else:  # destroy
                permission_classes = [permissions.IsAuthenticated, CanDeleteTicket]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all tickets
        if user.profile.role == 'admin':
            return Ticket.objects.all()
        
        # Support can see tickets assigned to them or unassigned
        if user.profile.role == 'support':
            return Ticket.objects.filter(Q(assigned_to=user) | Q(assigned_to=None))
        
        # Client can only see their own tickets
        return Ticket.objects.filter(created_by=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        ticket = self.get_object()
        
        # Only admin can assign tickets
        if request.user.profile.role != 'admin':
            return Response(
                {"detail": "You do not have permission to assign tickets."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the user to assign
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {"detail": "User ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(pk=user_id)
            # Only support users can be assigned tickets
            if not hasattr(user, 'profile') or user.profile.role != 'support':
                return Response(
                    {"detail": "Only support users can be assigned tickets."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            ticket.assigned_to = user
            ticket.save()
            
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter comments based on user role
        if user.profile.role == 'admin':
            # Admin can see all comments
            return Comment.objects.all()
        elif user.profile.role == 'support':
            # Support can see comments on tickets assigned to them
            return Comment.objects.filter(ticket__assigned_to=user)
        else:  # client
            # Client can only see comments on their own tickets
            return Comment.objects.filter(ticket__created_by=user)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# Template-based views
@method_decorator(login_required, name='dispatch')
class TicketListView(ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Filter based on user role
        if user.profile.role == 'admin':
            # Admin can see all tickets
            queryset = Ticket.objects.all()
        elif user.profile.role == 'support':
            # Support can see tickets assigned to them or unassigned
            queryset = Ticket.objects.filter(Q(assigned_to=user) | Q(assigned_to=None))
        else:  # client
            # Client can only see their own tickets
            queryset = Ticket.objects.filter(created_by=user)
        
        # Apply filters from form
        form = TicketFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            if form.cleaned_data.get('priority'):
                queryset = queryset.filter(priority=form.cleaned_data['priority'])
            if form.cleaned_data.get('category'):
                category_code = form.cleaned_data['category']
                queryset = queryset.filter(category__code=category_code)
            if form.cleaned_data.get('search'):
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_term) | 
                    Q(description__icontains=search_term) |
                    Q(ticket_id__icontains=search_term)
                )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TicketFilterForm(self.request.GET)
        return context

@method_decorator(login_required, name='dispatch')
class TicketDetailView(DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        
        # Check if user has permission to view this ticket
        if user.profile.role == 'admin':
            return obj
        elif user.profile.role == 'support' and (obj.assigned_to == user or obj.assigned_to is None):
            return obj
        elif user.profile.role == 'client' and obj.created_by == user:
            return obj
        else:
            messages.error(self.request, "You don't have permission to view this ticket.")
            return redirect('ticket_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all().order_by('-created_at')
        
        # Add assign form for admins
        if self.request.user.profile.role == 'admin':
            context['assign_form'] = TicketAssignForm()
        
        # Add status update form for admins and assigned support staff
        if self.request.user.profile.role == 'admin' or \
           (self.request.user.profile.role == 'support' and self.object.assigned_to == self.request.user):
            context['status_form'] = TicketStatusUpdateForm(initial={'status': self.object.status})
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Handle comment submission
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = self.object
                comment.author = request.user
                comment.save()
                messages.success(request, "Comment added successfully.")
                return redirect('ticket_detail', pk=self.object.pk)
        
        # Handle ticket assignment (admin only)
        elif 'assign_submit' in request.POST and request.user.profile.role == 'admin':
            assign_form = TicketAssignForm(request.POST)
            if assign_form.is_valid():
                self.object.assigned_to = assign_form.cleaned_data['assigned_to']
                self.object.save()
                messages.success(request, f"Ticket assigned to {self.object.assigned_to.username}.")
                return redirect('ticket_detail', pk=self.object.pk)
        
        # Handle status update (admin or assigned support)
        elif 'status_submit' in request.POST and \
             (request.user.profile.role == 'admin' or \
              (request.user.profile.role == 'support' and self.object.assigned_to == request.user)):
            status_form = TicketStatusUpdateForm(request.POST)
            if status_form.is_valid():
                old_status = self.object.status
                new_status = status_form.cleaned_data['status']
                self.object.status = new_status
                self.object.save()
                
                # Add a system comment about the status change
                if old_status != new_status:
                    Comment.objects.create(
                        ticket=self.object,
                        author=request.user,
                        content=f"Status changed from {dict(Ticket.STATUS_CHOICES)[old_status]} to {dict(Ticket.STATUS_CHOICES)[new_status]}"
                    )
                    messages.success(request, "Ticket status updated successfully.")
                
                return redirect('ticket_detail', pk=self.object.pk)
        
        return self.get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    success_url = reverse_lazy('ticket_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'open'
        
        if self.request.user.profile.role == 'client':
            form.instance.assigned_to = None
        
        category_obj = form.cleaned_data.get('category')
        department_obj = form.cleaned_data.get('department')
        
        if category_obj:
            form.instance.category = category_obj
        
        if department_obj:
            form.instance.department = department_obj
        
        messages.success(self.request, "Ticket created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TicketUpdateView(UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        
        # Check if user has permission to update this ticket
        if user.profile.role == 'admin':
            return obj
        elif user.profile.role == 'support' and obj.assigned_to == user:
            return obj
        elif user.profile.role == 'client' and obj.created_by == user and obj.status == 'open':
            # Clients can only edit their own open tickets
            return obj
        else:
            messages.error(self.request, "You don't have permission to edit this ticket.")
            return redirect('ticket_list')
    
    def form_valid(self, form):
    # If needed, update fields here (e.g., set updated_by, or other logic)
    
        category_obj = form.cleaned_data.get('category')
        department_obj = form.cleaned_data.get('department')
        
        if category_obj:
            form.instance.category = category_obj
        
        if department_obj:
            form.instance.department = department_obj

        messages.success(self.request, "Ticket updated successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class TicketDeleteView(DeleteView):
    model = Ticket
    template_name = 'tickets/ticket_confirm_delete.html'
    success_url = reverse_lazy('ticket_list')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        
        # Check if user has permission to delete this ticket
        if user.profile.role == 'admin':
            return obj
        elif user.profile.role == 'client' and obj.created_by == user and obj.status == 'open':
            # Clients can only delete their own open tickets
            return obj
        else:
            messages.error(self.request, "You don't have permission to delete this ticket.")
            return redirect('ticket_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Ticket deleted successfully.")
        return super().delete(request, *args, **kwargs)

@login_required
def ticket_assign(request, pk):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, pk=pk)
        if request.user.profile.role != 'admin':
            messages.error(request, 'You do not have permission to assign tickets.')
            return redirect('ticket_detail', pk=pk)

        assigned_to_id = request.POST.get('assigned_to')
        if assigned_to_id:
            assigned_user = get_object_or_404(User, pk=assigned_to_id)
            ticket.assigned_to = assigned_user
            ticket.save()
            messages.success(request, 'Ticket assigned successfully.')
        else:
            messages.error(request, 'Please select a support agent to assign.')

    return redirect('ticket_detail', pk=pk)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def ticket_update_status(request, pk):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, pk=pk)

        if request.user.profile.role not in ['admin', 'support']:
            messages.error(request, 'You do not have permission to update ticket status.')
            return redirect('ticket_detail', pk=pk)

        new_status = request.POST.get('status')
        if new_status in dict(Ticket.STATUS_CHOICES).keys():
            ticket.status = new_status
            ticket.save()
            messages.success(request, 'Ticket status updated successfully.')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('ticket_detail', pk=pk)


@login_required
def add_comment(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    # Check if user has permission to comment on this ticket
    user = request.user
    if user.profile.role == 'admin':
        pass  # Admin can comment on any ticket
    elif user.profile.role == 'support' and (ticket.assigned_to == user or ticket.assigned_to is None):
        pass  # Support can comment on assigned tickets or unassigned tickets
    elif user.profile.role == 'client' and ticket.created_by == user:
        pass  # Client can comment on their own tickets
    else:
        messages.error(request, "You don't have permission to comment on this ticket.")
        return redirect('ticket_list')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added successfully.")
    
    return redirect('ticket_detail', pk=ticket_id)

@login_required
def home_view(request):
    user = request.user
    context = {}
    
    # Add statistics for admin dashboard
    if user.profile.role == 'admin':
        context['total_tickets'] = Ticket.objects.count()
        context['total_users'] = User.objects.count()
        context['open_tickets'] = Ticket.objects.filter(status='open').count()
        context['resolved_tickets'] = Ticket.objects.filter(status='resolved').count()
        
        # Tickets by department
        departments = Department.objects.annotate(ticket_count=Count('tickets'))
        context['departments'] = departments
        
        # Tickets by category
        categories = Category.objects.annotate(ticket_count=Count('tickets'))
        context['categories'] = categories
    
    # For support staff
    elif user.profile.role == 'support':
        context['assigned_tickets'] = Ticket.objects.filter(assigned_to=user).count()
        context['open_assigned_tickets'] = Ticket.objects.filter(assigned_to=user, status='open').count()
        context['unassigned_tickets'] = Ticket.objects.filter(assigned_to=None).count()
    
    # For clients
    else:
        context['my_tickets'] = Ticket.objects.filter(created_by=user).count()
        context['open_tickets'] = Ticket.objects.filter(created_by=user, status='open').count()
        context['resolved_tickets'] = Ticket.objects.filter(created_by=user, status='resolved').count()
    
    return render(request, 'home.html', context)
