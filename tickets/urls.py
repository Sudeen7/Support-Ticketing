from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # API ViewSets
    DepartmentViewSet, CategoryViewSet, TicketViewSet, CommentViewSet,
    # Template Views
    TicketListView, TicketDetailView, TicketCreateView, TicketUpdateView, TicketDeleteView,
    add_comment, home_view, ticket_assign, ticket_update_status
)

# API router
router = DefaultRouter()
router.register(r'api/departments', DepartmentViewSet)
router.register(r'api/categories', CategoryViewSet)
router.register(r'api/tickets', TicketViewSet)
router.register(r'api/comments', CommentViewSet)

# Template URLs
template_urlpatterns = [
    path('', home_view, name='home'),
    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('tickets/new/', TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket_update'),
    path('tickets/<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket_delete'),
    path('tickets/<int:ticket_id>/comment/', add_comment, name='add_comment'),
    path('tickets/<int:pk>/assign/', ticket_assign, name='ticket_assign'),
    path('tickets/<int:pk>/update-status/', ticket_update_status, name='ticket_update_status'),
]

urlpatterns = template_urlpatterns + [
    path('', include(router.urls)),
]