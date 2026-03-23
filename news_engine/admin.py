from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Article, Category, Publisher, Comment, Newsletter, Like


# 1. CustomUser Management
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "role", "publisher", "is_staff"]

    fieldsets = UserAdmin.fieldsets + (
        ("Professional Info", {"fields": ("role", "publisher", "bio")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Professional Info", {"fields": ("role", "publisher", "bio")}),
    )


# 2. Article Management (Fixed 'publisher' to 'author')
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "publisher_house",
        "category",
        "is_approved",
        "created_at",
    )
    list_filter = ("is_approved", "category", "publisher_house")
    search_fields = ("title", "content")
    actions = ["approve_articles"]

    @admin.action(description="Mark selected articles as approved")
    def approve_articles(self, request, queryset):
        queryset.update(is_approved=True)


# 3. Publisher Management
@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# 4. Category Management
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# 5. Comment Management
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "article", "created_at")
    list_filter = ("created_at", "article")


# 6. Simple Registrations
admin.site.register(Newsletter)
admin.site.register(Like)
