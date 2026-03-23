from django.apps import AppConfig
from django.db.models.signals import post_migrate


class NewsEngineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news_engine"

    def ready(self):
        # 1. Connect the group/permission creator to the post_migrate signal
        post_migrate.connect(create_groups_and_permissions, sender=self)

        # 2. Import your email/automation signals
        try:
            import news_engine.signals
        except ImportError:
            pass


def create_groups_and_permissions(sender, **kwargs):
    """
    Ensures User Groups exist and have the right permissions
    automatically after 'python manage.py migrate' is run.
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    groups_config = {
        "Editor": [
            "view_article",
            "change_article",
            "delete_article",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
        "Journalist": [
            "add_article",
            "view_article",
            "change_article",
            "delete_article",
            "add_newsletter",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
        "Reader": ["view_article", "view_newsletter"],
    }

    for group_name, perms in groups_config.items():
        group, created = Group.objects.get_or_create(name=group_name)

        for perm_code in perms:
            model_name = "article" if "article" in perm_code else "newsletter"

            try:
                content_type = ContentType.objects.get(
                    app_label="news_engine", model=model_name
                )
                permission = Permission.objects.get(
                    codename=perm_code, content_type=content_type
                )
                group.permissions.add(permission)
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                # This helps debug if migrations haven't run yet
                continue
