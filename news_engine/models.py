from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings
import tweepy


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="reader")
    bio = models.TextField(blank=True, null=True)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, blank=True, related_name="followers"
    )


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="article_images/", blank=True, null=True)
    publisher_house = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tweeted = models.BooleanField(default=False)

    def post_to_twitter(self):
        """Logic to post to X using Tweepy API v2 - Must be INSIDE the class"""
        # Safety check: Don't run if keys are still placeholders in settings.py
        if (
            not hasattr(settings, "TWITTER_API_KEY")
            or "your_" in settings.TWITTER_API_KEY
        ):
            print("Twitter keys not configured yet. Skipping post.")
            return

        if self.tweeted or not self.is_approved:
            return

        try:
            client = tweepy.Client(
                bearer_token=getattr(settings, "TWITTER_BEARER_TOKEN", None),
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            )

            article_url = f"http://127.0.0.1:8000/article/{self.id}/"
            tweet_text = f"🚨 NEW STORY: {self.title}\nRead more: {article_url}"

            client.create_tweet(text=tweet_text)

            self.tweeted = True
            self.save(update_fields=["tweeted"])
        except Exception as e:
            print(f"X Posting Error: {e}")

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Subscription(models.Model):
    reader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_subscriptions",
    )
    journalist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="journalist_subscriptions",
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="publisher_subscriptions",
    )

    def __str__(self):
        target = self.journalist.username if self.journalist else self.publisher.name
        return f"{self.reader.username} follows {target}"


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")
