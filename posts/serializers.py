from rest_framework import serializers
from .models import Post, Comment, Category

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'post', 'comment_content', 'user', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_slug', 'category_name']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)  # Nested serializer to include comments
    category = CategorySerializer(read_only=True)  # Single category (not many=True)

    class Meta:
        model = Post
        fields = ['post_id', 'user', 'post_content', 'post_image_url', 'post_like_count',
                  'post_liked_by', 'post_disliked_by', 'category', 'comments', 'created_at', 'updated_at']

    def get_comments(self, post):
        return CommentSerializer(post.comments.all(), many=True).data  # Fetch all comments for the post
