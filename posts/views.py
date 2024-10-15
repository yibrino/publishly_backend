from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Post,Comment,Category
from users.models import User
from .serializers import PostSerializer,CommentSerializer,CategorySerializer
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404

from django.http import JsonResponse

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def create(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')  # Get the user_id from the URL
        try:
            # Fetch the user based on the user_id
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Capture post data from the request
        post_content = request.data.get('post_content')
        post_image_url = request.data.get('post_image_url')
        category_id = request.data.get('category_id')

        # Validate required fields
        if not post_content or not post_image_url:
            return Response({"error": "Missing required fields: post_content or post_image_url"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the Post object
            post = Post.objects.create(
                user=user,
                post_content=post_content,
                post_image_url=post_image_url,
                category_id=category_id,
            )

            # Add users to the post_liked_by ManyToMany field
            # if post_liked_by:
            #     liked_users = User.objects.filter(user_id__in=post_liked_by)  # Get the users from the list of IDs
            #     post.post_liked_by.add(*liked_users)  # Add the users to the ManyToMany field

            # # Save the post
            post.save()

            # Serialize the post object
            post_serializer = PostSerializer(post)

            # Return success message with the serialized post data
            return JsonResponse({
                'post': post_serializer.data  # Serialized post data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    # def retrieve(self, request, pk=None):
    #     try:
    #         profile = Profile.objects.get(pk=pk)
    #     except Profile.DoesNotExist:
    #         return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = ProfileSerializer(profile)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # Update A post
    
    def update(self, request, pk=None):
    # Get the post_id from the URL        
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        # Capture profile data from the request
        post_content = request.data.get('post_content')
        post_image_url = request.data.get('post_image_url')

        # Validate required fields
        if not post_content :
            return Response({"error": "Missing required fields: post content "}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Update the post with new data
            post.post_content = post_content
            post.post_image_url = post_image_url
            post.save()

            # Serialize the updated post object
            post_serializer = PostSerializer(post)

            # Return success message with the serialized post data
            return JsonResponse({
                'post': post_serializer.data  # Serialized post data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

   
    # Delete A post
    def delete(self, request, pk=None):
      try:
        post= Post.objects.get(pk=pk)
        post.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)
      except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Like a post

@api_view(['POST'])
def like_post(request, post_id):
    try:
        # Get the post
        post = get_object_or_404(Post, post_id=post_id)
        
        # Get the user who is liking the post
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, user_id=user_id)

        # Remove the user from the disliked list if they disliked the post
        if user in post.post_disliked_by.all():
            post.post_disliked_by.remove(user)

        # Check if the user has already liked the post
        if user in post.post_liked_by.all():
            post.post_liked_by.remove(user)
            post.post_like_count -= 1
            post.save()
            return Response({"message": "Post unliked successfully."}, status=status.HTTP_200_OK)
        else:
            post.post_liked_by.add(user)
            post.post_like_count += 1
            post.save()
            return Response({"message": "Post liked successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# Dislike a post
@api_view(['POST'])
def dislike_post(request, post_id):
    try:
        # Get the post
        post = get_object_or_404(Post, post_id=post_id)
        
        # Get the user who is disliking the post
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, user_id=user_id)

        # Remove the user from the liked list if they liked the post
        if user in post.post_liked_by.all():
            post.post_liked_by.remove(user)
            post.post_like_count -= 1

        # Check if the user has already disliked the post
        if user in post.post_disliked_by.all():
            post.post_disliked_by.remove(user)
            post.save()
            return Response({"message": "Post undisliked successfully."}, status=status.HTTP_200_OK)
        else:
            post.post_disliked_by.add(user)
            post.save()
            return Response({"message": "Post disliked successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Comment
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def create(self, request, *args, **kwargs):
        # Extract post_id from the URL kwargs
        post_id = kwargs.get('post_id')
        
        # Get the authenticated user (who is making the comment), using your custom user model

        try:
            # Fetch the post based on the post_id
            post = Post.objects.get(post_id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        # Capture the comment content from the request data
        comment_content = request.data.get('comment_content')
        commented_by = request.data.get('commented_by')  # Assume this is a user ID
        # Validate that comment_content is provided
        if not comment_content:
            return Response({"error": "Missing required field: comment_content"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the user instance using commented_by
            user = User.objects.get(user_id=commented_by)
            
            # Create the Comment object
            comment = Comment.objects.create(
                post=post,  # Associate the comment with the post
                user=user,  # Use the User instance
                comment_content=comment_content
            )

            # Serialize the newly created comment
            comment_serializer = CommentSerializer(comment)

            # Return success response with serialized comment data
            return JsonResponse({
                'comment': comment_serializer.data  # Serialized comment data
            }, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # Retrive A comment

    def retrieve(self, request, pk=None):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
# 
    # Update comment
    def update(self, request, *args, **kwargs):
        # Extract pk from the URL kwargs, as pk is passed in the URL
        comment_id = kwargs.get('pk')  # pk refers to the primary key in the URL pattern
        
        try:
            # Fetch the comment based on the comment_id (primary key)
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get the authenticated user (the one who is updating the comment)
        commented_by = request.data.get('commented_by')  # Assume this is a user ID

        # Check if the user who is updating the comment is the same as the one who created it
        try:
            user = User.objects.get(user_id=commented_by)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != user:
            return Response({"error": "You are not authorized to update this comment."}, status=status.HTTP_403_FORBIDDEN)

        # Capture the updated comment content from the request data
        comment_content = request.data.get('comment_content')

        # Validate that comment_content is provided
        if not comment_content:
            return Response({"error": "Missing required field: comment_content"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Update the comment content
            comment.comment_content = comment_content
            comment.save()

            # Serialize the updated comment
            comment_serializer = CommentSerializer(comment)

            # Return success response with serialized updated comment data
            return JsonResponse({
                'comment': comment_serializer.data  # Serialized updated comment data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
    
    def delete(self, request, pk=None):
      try:
        comment= Comment.objects.get(pk=pk)
        comment.delete()
        return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)
      except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Category View

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)
        
    def create(self, request, *args, **kwargs):

        # Capture category data from the request
        category_slug = request.data.get('category_slug')
        category_name = request.data.get('category_name')
    
        # Validate required fields
        if not category_slug or not category_name:
            return Response({"error": "Missing required fields: category_slug or category_name"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the category object
            category = Category.objects.create(
                category_slug=category_slug,
                category_name=category_name,
            )

      

            # Serialize the category object
            category_serializer = CategorySerializer(category)

            # Return success message with the serialized category data
            return JsonResponse({
                'post': category_serializer.data  # Serialized category data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  

    # Update Category
    
    def update(self, request, pk=None):
        try:
            # Get the category by primary key (pk)
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        # Capture category data from the request
        category_slug = request.data.get('category_slug')
        category_name = request.data.get('category_name')

        # Update the category with the new data
        category.category_slug = category_slug  # This should update the slug field
        category.category_name = category_name  # This updates the name field
        category.save()

        # Serialize the updated category object
        category_serializer = CategorySerializer(category)

        # Return success message with the serialized category data
        return JsonResponse({
            'category': category_serializer.data  # Serialized category data
        }, status=status.HTTP_200_OK)




   
    # Delete Category
    def delete(self, request, pk=None):
      try:
        category= Category.objects.get(pk=pk)
        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_200_OK)
      except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
      except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    