from rest_framework import serializers
from .models import CustomUser, Article, Category, Comment, Newsletter, Publisher

# --- ACCOUNT SERIALIZERS ---


class RegisterSerializer(serializers.ModelSerializer):
    """Handles API-based user registration."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "password", "email", "role")

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            role=validated_data.get("role", "Reader"),
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role", "bio"]
        read_only_fields = ["username", "email"]


# --- CORE ENGINE SERIALIZERS ---


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "article", "author_name", "content", "created_at"]


class ArticleSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source="author.username")
    category_name = serializers.ReadOnlyField(source="category.name")
    like_count = serializers.ReadOnlyField(source="total_likes")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "image",
            "author_name",
            "category",
            "category_name",
            "comments",
            "like_count",
            "created_at",
            "is_approved",
        ]
        read_only_fields = ["is_approved"]


class NewsletterSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source="creator.username")

    class Meta:
        model = Newsletter
        fields = ["id", "title", "content", "creator_name", "created_at"]
