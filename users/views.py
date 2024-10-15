from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.http import require_http_methods

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import User,Profile,Follower
from .serializers import UserSerializer,ProfileSerializer,FollowerUserSerializer,UserSignupSerializer,FollowerSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404

from django.http import JsonResponse
# UserViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        username = request.data.get('user_username')
        firstname=request.data.get('user_firstname')
        lastname=request.data.get('user_lastname')
        email = request.data.get('user_email')
        password = request.data.get('password')
        


        if not username or not email or not password:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(user_email=email).exists():
            return Response({"error": "A User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the new user object
        user = User(
            user_firstname=firstname,
            user_lastname=lastname,
            user_username=username,
            user_email=email,
            password=make_password(password)  # Hash the password before saving
        )

        try:
            user.save()  # Save the new user to the database

            # Serialize the user object
            serializer = UserSignupSerializer(user)

            # Generate JWT token for the user
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Return success message, the serialized user object, and the JWT token
            return JsonResponse({
                'foundUser': serializer.data,  # Return the entire serialized user object
                "encodedToken": access_token  # JWT token
            }, status=status.HTTP_201_CREATED)
          
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
  
        user_username = request.data.get('user_username')
        user_email = request.data.get('user_email')
        password = request.data.get('user_password')

        # Validate required fields
        if not user_username or not user_email or not password  :
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(user, data=request.data, partial=True)  # Use partial=True for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
      try:
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
      except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
@csrf_exempt  # Exempting CSRF for APIs
@require_http_methods(["POST"])  # Only allow POST requests
def login_user(request):
    try:
        # Parse the JSON request body
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

    # Extract email and password from request data
    email = data.get('user_email')
    password = data.get('password')

    # Ensure both email and password are provided
    if not email :
        return JsonResponse({"error": "Email required"}, status=status.HTTP_400_BAD_REQUEST)
    if  not password:
        return JsonResponse({"error": " password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the user based on email
        user = User.objects.get(user_email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the password using check_password
    if not user.check_password(password):  # Use this method to check the hashed password
     return JsonResponse({"error": "Error to while checking the  password"}, status=status.HTTP_400_BAD_REQUEST)

    # Generate JWT token for the user
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Return success message and the JWT token
    return JsonResponse({
        'foundUser': {
                'username': user.user_username,
                'email': user.user_email,
                'id': user.user_id,
                'is_superuser':user.is_superuser,
            },
        "encodedToken": access_token  # JWT token
    }, status=status.HTTP_200_OK)

# ProfileViewSet
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def create(self, request, *args, **kwargs):
        pk = kwargs.get('pk')  # Get the pk (user_id) from the URL
        try:
            # Fetch the user based on the pk (user_id)
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Capture profile data from the request
        user_bio = request.data.get('user_bio', '')
        user_website = request.data.get('user_website', '')
        user_profile_picture = request.data.get('user_profile_picture', 'https://via.placeholder.com/150')

        # Validate required fields
        if not user_bio or not user_website:
            return Response({"error": "Missing required fields: user_bio or user_website."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the associated profile for the user
            profile = Profile.objects.create(
                user=user,
                user_bio=user_bio,
                user_website=user_website,
                user_profile_picture=user_profile_picture
            )

            profile.save()  # Save the profile after setting followers and following

            # Serialize the profile object
            profile_serializer = ProfileSerializer(profile)

            # Return success message with the serialized profile data
            return JsonResponse({
                'profile': profile_serializer.data  # Serialized profile data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
    # Get the profile_id from the URL
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Capture profile data from the request
        user_bio = request.data.get('user_bio', profile.user_bio)
        user_website = request.data.get('user_website', profile.user_website)
        user_profile_picture = request.data.get('user_profile_picture', profile.user_profile_picture)

        # Validate required fields
        if not user_bio or not user_website:
            return Response({"error": "Missing required fields: firstname or lastname."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Update the profile with new data
            profile.user_bio = user_bio
            profile.user_website = user_website
            profile.user_profile_picture = user_profile_picture
            profile.save()

            # Serialize the updated profile object
            profile_serializer = ProfileSerializer(profile)

            # Return success message with the serialized profile data
            return JsonResponse({
                'profile': profile_serializer.data  # Serialized profile data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

   
    
    def delete(self, request, pk=None):
      try:
        profile= Profile.objects.get(pk=pk)
        profile.delete()
        return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_200_OK)
      except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

    #Followers
class FollowerViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = FollowerUserSerializer
        permission_classes = [permissions.AllowAny]

        def list(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            serializer = FollowerUserSerializer(queryset, many=True)
            return Response(serializer.data)
        

        def create(self, request, pk=None, *args, **kwargs):
        # `pk` is the ID of the user to be followed, coming from the URL
          follower_user_id = request.data.get('follower_user_id')  # ID of the follower user

        # Ensure the follower_user_id is provided
          if not follower_user_id:
            return Response({"error": "follower_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the user isn't trying to follow themselves
          if pk == follower_user_id:
            return Response({"error": "A user cannot follow themselves."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user to be followed and the follower user
          user = get_object_or_404(User, pk=pk)
          follower_user = get_object_or_404(User, pk=follower_user_id)

        # Check if the follow relationship already exists
          if Follower.objects.filter(user=user, follower_user=follower_user).exists():
            return Response({"error": "This follow relationship already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the follow relationship
          follower = Follower(user=user, follower_user=follower_user)
          follower.save()

        # Serialize the newly created follower relationship
          serializer = FollowerSerializer(follower)

        # Return success response
          return Response(serializer.data, status=status.HTTP_201_CREATED)

        def destroy(self, request, pk=None, *args, **kwargs):
        # `pk` is the ID of the user to be unfollowed, coming from the URL
          follower_user_id = request.data.get('follower_user_id')  # ID of the follower user

        # Ensure the follower_user_id is provided
          if not follower_user_id:
            return Response({"error": "follower_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user to be unfollowed and the follower user
          user = get_object_or_404(User, pk=pk)
          follower_user = get_object_or_404(User, pk=follower_user_id)

        # Check if the follow relationship exists
          try:
            follower = Follower.objects.get(user=user, follower_user=follower_user)
            follower.delete()
            return Response({"message": "Unfollowed successfully."}, status=status.HTTP_200_OK)
          except Follower.DoesNotExist:
            return Response({"error": "Follow relationship does not exist."}, status=status.HTTP_400_BAD_REQUEST)