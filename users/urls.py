from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet,login_user,ProfileViewSet,FollowerViewSet
router = DefaultRouter()
router.register(r'users/', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # User
    path('users/', UserViewSet.as_view({'get': 'list'}), name='users-list'),
    path('users/create/', UserViewSet.as_view({'post': 'create'}), name='user-create'),
    path('user/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='user-retrieve'),
    path('user/<int:pk>/', UserViewSet.as_view({'delete': 'delete'}), name='user-delete'),
    path('user/update/<int:pk>/', UserViewSet.as_view({'put': 'update'}), name='user-update'),
   path('user/login/',login_user, name="user-login" ),

    # Profile
    
    path('profiles/', ProfileViewSet.as_view({'get': 'list'}), name='profiles-list'),  # List all profiles
    path('profile/<int:pk>/', ProfileViewSet.as_view({'get': 'retrieve'}), name='profile-retrieve'),  # Retrieve a specific user's profile
    path('profile/create/<int:pk>/', ProfileViewSet.as_view({'post': 'create'}), name='profile-create'),  # Create a profile for a specific user
    path('profile/update/<int:pk>/', ProfileViewSet.as_view({'put': 'update'}), name='profile-update'),  # Update a specific user's profile
    path('profile/<int:pk>/', ProfileViewSet.as_view({'delete': 'delete'}), name='profile-delete'),  # Delete a specific user's profile
   
    # Followers
    path('followers/', FollowerViewSet.as_view({'get': 'list'}), name='followers-list'),  # List all profiles
    path('user/follow/<int:pk>/', FollowerViewSet.as_view({'post': 'create'}), name='user-follow'), 
    path('user/unfollow/<int:pk>/', FollowerViewSet.as_view({'delete': 'destroy'}), name='unfollow-user'), 

]
