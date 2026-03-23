import requests
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Article, CustomUser, Newsletter

# --- 1. STATE TRACKING ---


@receiver(pre_save, sender=Article)
def track_approval_status(sender, instance, **kwargs):
    """
    Stores the previous approval state to detect the exact moment an
    article changes from 'Pending' to 'Approved'.
    """
    if instance.pk:
        try:
            old_obj = Article.objects.get(pk=instance.pk)
            instance._was_approved = old_obj.is_approved
        except Article.DoesNotExist:
            instance._was_approved = False
    else:
        instance._was_approved = False


# --- 2. ARTICLE APPROVAL WORKFLOW ---


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """
    Sends notifications only when an article is approved by an editor.
    """
    was_previously_approved = getattr(instance, "_was_approved", False)
    is_just_approved = instance.is_approved and not was_previously_approved

    if is_just_approved:
        print(
            f"NOTIF: Notifying {instance.author.email} that '{instance.title}' is live."
        )

        subscribers = CustomUser.objects.filter(subscribed_journalists=instance.author)
        recipient_list = [user.email for user in subscribers if user.email]

        if recipient_list:
            send_mail(
                subject=f"New Article: {instance.title}",
                message=f"{instance.author.username} just published a new story!\n\nRead it now on GNN.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True,
            )

        try:
            requests.post(
                "https://api.twitter.com/2/tweets",
                json={"text": f"New Story: {instance.title}"},
                headers={"Authorization": "Bearer YOUR_TOKEN"},
                timeout=1,
            )
        except Exception:
            print("Social media sync skipped.")


# --- 3. NEWSLETTER AUTOMATION ---


@receiver(post_save, sender=Newsletter)
def send_newsletter_email(sender, instance, created, **kwargs):
    """
    Sends newsletter content to followers immediately upon creation.
    FIXED: Uses 'creator' instead of 'author' to match your Newsletter model.
    """
    if created:

        journalist = instance.creator

        subscribers = CustomUser.objects.filter(subscribed_journalists=journalist)
        recipient_list = [sub.email for sub in subscribers if sub.email]
        print("recipient_list", recipient_list)

        if recipient_list:
            send_mail(
                subject=f"Newsletter from {journalist.username}: {instance.title}",
                message=instance.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            print(f"SUCCESS: Newsletter sent to {len(recipient_list)} subscribers.")
