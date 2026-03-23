import random
from django.core.management.base import BaseCommand
from news_engine.models import CustomUser, Category, Article, Publisher


class Command(BaseCommand):
    help = "Populates the database with sample news data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Create Categories
        categories = ["Politics", "Technology", "Health", "Science", "Sports", "World"]
        cat_objs = [Category.objects.get_or_create(name=cat)[0] for cat in categories]

        # 2. Create a Publisher
        publisher, _ = Publisher.objects.get_or_create(
            name="Global News Network", website="https://gnn.com"
        )

        # 3. Create Journalists
        journalists = []
        for i in range(3):
            user, created = CustomUser.objects.get_or_create(
                username=f"journalist_{i}", email=f"j{i}@gnn.com", role="journalist"
            )
            if created:
                user.set_password("gnnpassword123")
                user.save()
            journalists.append(user)

        # 4. Create Articles
        titles = [
            "AI Breakthrough: Machines Learn Empathy",
            "Global Summit Addresses Climate Urgency",
            "New Mars Rover Sends Back Stunning Images",
            "Local Team Wins Championship in Overtime",
            "The Future of Remote Work: A Deep Dive",
            "Breakthrough in Fusion Energy Research",
            "Global Markets React to New Tech IPO",
            "Hidden Ruins Discovered in the Amazon",
        ]

        for title in titles:
            Article.objects.get_or_create(
                title=title,
                content="This is a sample article body. " * 50,
                author=random.choice(journalists),
                category=random.choice(cat_objs),
                is_approved=True,
            )

        self.stdout.write(
            self.style.SUCCESS("Successfully seeded GNN with sample data!")
        )
