from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # --- Authentication (HTML) ---
    path("register/", views.register_html, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="news_engine/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # --- Core UI Routes ---
    path("", views.home, name="home"),
    path("news/", views.ArticleListView.as_view(), name="article_list"),
    path("news/<int:pk>/", views.article_detail, name="article_detail"),
    path("feed/", views.user_feed, name="user_feed"),
    path("journalist/<int:pk>/", views.journalist_detail, name="journalist_detail"),
    # --- Article Management (Journalists) ---
    path("news/submit/", views.ArticleCreateView.as_view(), name="submit_article"),
    path("news/<int:pk>/edit/", views.ArticleUpdateView.as_view(), name="edit_article"),
    path(
        "news/<int:pk>/delete/",
        views.ArticleDeleteView.as_view(),
        name="delete_article",
    ),
    # --- Newsletter Management ---
    path(
        "newsletter/new/",
        views.NewsletterCreateView.as_view(),
        name="submit_newsletter",
    ),
    path(
        "newsletter/<int:pk>/edit/",
        views.NewsletterUpdateView.as_view(),
        name="edit_newsletter",
    ),
    path(
        "newsletter/<int:pk>/delete/",
        views.NewsletterDeleteView.as_view(),
        name="delete_newsletter",
    ),
    # --- Editor Desk (Workflow) ---
    path("editor/desk/", views.editor_dashboard, name="editor_dashboard"),
    path(
        "editor/approve/<int:article_id>/",
        views.approve_article_html,
        name="approve_article",
    ),
    path(
        "editor/reject/<int:article_id>/",
        views.reject_article_html,
        name="reject_article",
    ),
    # --- Social Actions ---
    path(
        "subscribe/<str:target_type>/<int:target_id>/",
        views.subscribe,
        name="subscribe",
    ),
    # --- REST API Endpoints ---
    path("api/register/", views.RegisterAPIView.as_view(), name="api_register"),
    path("api/articles/", views.ArticleListCreate.as_view(), name="api_articles"),
    path("api/feed/", views.UserFeedAPIView.as_view(), name="api_user_feed"),
    path(
        "api/articles/<int:pk>/like/",
        views.LikeArticleAPIView.as_view(),
        name="api_like_article",
    ),
    # --- API Documentation (Swagger/OpenAPI) ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
