from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Article, Category, Publisher

User = get_user_model()


class NewsEngineFinalTests(APITestCase):
    def setUp(self):
        # 1. Create the Publisher (This is the "Publishing House" the instructor wants)
        self.pub_house = Publisher.objects.create(
            name="Daily Planet", website="https://dailyplanet.com"
        )

        # 2. Create Users
        self.journalist = User.objects.create_user(
            username="journalist_user",
            role="Journalist",
            password="pass",
            email="journalist@test.com",
        )
        self.reader = User.objects.create_user(
            username="reader_user",
            role="Reader",
            password="pass",
            email="reader@test.com",
        )

        # 3. Create Category and Article
        self.cat = Category.objects.create(name="Tech")
        self.article = Article.objects.create(
            title="Initial Title",
            content="Initial Content",
            publisher=self.journalist,
            publisher_house=self.pub_house,
            category=self.cat,
            is_approved=False,
        )

        self.list_url = reverse("article-list-create")

    def test_reader_cannot_post_article(self):
        """Proof of RBAC: Readers get 403 when trying to POST."""
        self.client.force_authenticate(user=self.reader)
        data = {
            "title": "Unauthorized News",
            "content": "Should not work",
            "category": self.cat.id,
            "publisher_house": self.pub_house.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_signal_fires_only_on_approval_transition(self):
        """Proof of Bug Fix: Email fires only on unapproved -> approved transition"""
        mail.outbox = []
        self.reader.subscribed_journalists.add(self.journalist)

        # Trigger approval
        article_to_approve = Article.objects.get(pk=self.article.pk)
        article_to_approve.is_approved = True
        article_to_approve.save()

        self.assertEqual(
            len(mail.outbox), 1, "Signal failed to send email on approval transition."
        )

        # Ensure no duplicate on edit
        article_to_approve.title = "Updated Title"
        article_to_approve.save()
        self.assertEqual(len(mail.outbox), 1, "Duplicate email sent on article edit!")

    def test_unapproved_articles_hidden_from_api(self):
        """Proof of Data Integrity: Unapproved articles are filtered out from public feed"""
        self.client.force_authenticate(user=self.reader)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 0)
