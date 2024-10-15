from rest_framework import serializers

from .models import User,Profile,Follower


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id','user_firstname','user_lastname','is_superuser', 'user_username', 'user_email']

class UserSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id','is_superuser', 'user_firstname','user_lastname','user_username', 'user_email', 'followers', 'following',"created_at"]

    def get_followers(self, obj):
        # Get the list of users who follow this user
        followers = Follower.objects.filter(user=obj)  # This filters Follower records where the user is being followed.
        return FollowerUserSerializer([f.follower_user for f in followers], many=True).data

    def get_following(self, obj):
        # Get the list of users this user is following
        following = Follower.objects.filter(follower_user=obj)  # This filters Follower records where the user is the follower.
        return FollowerUserSerializer([f.user for f in following], many=True).data
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'profile_id',
            'user',
            'user_bio',
            'user_website',
            'user_profile_picture',
            'created_at',
            'updated_at'
        ]

class FollowerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_username']


class FollowerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Follower
        fields = ['follower_id', 'user', 'follower_user', 'followed_at']

