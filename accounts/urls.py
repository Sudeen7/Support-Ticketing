from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    # API views
    RegisterAPIView, UserListView, UserDetailView, UserProfileAPIUpdateView,
    # Template views
    LoginView, logout_view, RegisterView, ProfileView, ProfileUpdateView
)

# API URLs
api_urlpatterns = [
    # Authentication endpoints
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('api/profile/', UserProfileAPIUpdateView.as_view(), name='api-profile-update'),
]

# Template URLs
urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Profile management
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
] + api_urlpatterns