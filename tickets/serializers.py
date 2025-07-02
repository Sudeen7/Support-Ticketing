from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Category, Ticket, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    ticket_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = ['id', 'ticket', 'ticket_id', 'author', 'author_id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'ticket', 'author']
    
    def create(self, validated_data):
        # Get the current user from the context
        user = self.context['request'].user
        validated_data['author'] = user
        
        # If ticket_id is provided, use it
        ticket_id = validated_data.pop('ticket_id', None)
        if ticket_id:
            from .models import Ticket
            try:
                ticket = Ticket.objects.get(pk=ticket_id)
                validated_data['ticket'] = ticket
            except Ticket.DoesNotExist:
                raise serializers.ValidationError({"ticket_id": "Ticket does not exist"})
        
        return super().create(validated_data)

class TicketListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'assigned_to',
            'category', 'department', 'status', 'status_display',
            'priority', 'priority_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

class TicketDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    comments = CommentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'assigned_to', 'assigned_to_id',
            'category', 'category_id', 'department', 'department_id', 'status', 'status_display',
            'priority', 'priority_display', 'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        # Get the current user from the context
        user = self.context['request'].user
        validated_data['created_by'] = user
        
        # Handle foreign key relationships
        self._handle_foreign_keys(validated_data)
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle foreign key relationships
        self._handle_foreign_keys(validated_data)
        
        return super().update(instance, validated_data)
    
    def _handle_foreign_keys(self, validated_data):
        # Handle assigned_to
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        if assigned_to_id is not None:
            try:
                assigned_to = User.objects.get(pk=assigned_to_id)
                validated_data['assigned_to'] = assigned_to
            except User.DoesNotExist:
                raise serializers.ValidationError({"assigned_to_id": "User does not exist"})
        
        # Handle category
        category_id = validated_data.pop('category_id', None)
        if category_id is not None:
            try:
                category = Category.objects.get(pk=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({"category_id": "Category does not exist"})
        
        # Handle department
        department_id = validated_data.pop('department_id', None)
        if department_id is not None:
            try:
                department = Department.objects.get(pk=department_id)
                validated_data['department'] = department
            except Department.DoesNotExist:
                raise serializers.ValidationError({"department_id": "Department does not exist"})