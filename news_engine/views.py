from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings

# REST Framework Imports
from rest_framework import generics, permissions, filters, status, exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend

# Local Imports
from .models import Article, Comment, Like, Newsletter, Publisher, Subscription
from .forms import ArticleSubmissionForm, CommentForm, CustomUserCreationForm
from .serializers import ArticleSerializer, RegisterSerializer, CommentSerializer

User = get_user_model()

# --- PERMISSION HELPERS ---


def is_editor(user):
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser
        or user.is_staff
        or getattr(user, "role", "").lower() == "editor"
    )


class ContentAccessMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        owner = getattr(obj, "author", getattr(obj, "creator", None))
        return is_editor(self.request.user) or owner == self.request.user


# --- AUTHENTICATION & UI ---


def register_html(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group_name = user.role.capitalize()
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            login(request, user)
            messages.success(request, f"Welcome! You are registered as a {user.role}.")
            return redirect("article_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "news_engine/register.html", {"form": form})


def home(request):
    return redirect("article_list")


# --- CORE NEWS VIEWS ---


class ArticleListView(ListView):
    model = Article
    template_name = "news_engine/article_list.html"
    context_object_name = "articles"
    paginate_by = 6

    def get_queryset(self):
        queryset = Article.objects.filter(is_approved=True).order_by("-created_at")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(category__name__icontains=query)
            )
        return queryset


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all().order_by("-created_at")
    if request.method == "POST" and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect("article_detail", pk=article.pk)
    else:
        form = CommentForm()
    return render(
        request,
        "news_engine/article_detail.html",
        {"article": article, "comments": comments, "comment_form": form},
    )


# --- ARTICLE WORKFLOW ---


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleSubmissionForm
    template_name = "news_engine/submit_article.html"
    success_url = reverse_lazy("article_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_approved = False
        messages.success(self.request, "Article submitted! Awaiting Editor approval.")
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, ContentAccessMixin, UpdateView):
    model = Article
    fields = ["title", "content", "category", "image"]
    template_name = "news_engine/submit_article.html"
    success_url = reverse_lazy("article_list")


class ArticleDeleteView(LoginRequiredMixin, ContentAccessMixin, DeleteView):
    model = Article
    template_name = "news_engine/article_confirm_delete.html"
    success_url = reverse_lazy("article_list")


# --- NEWSLETTER LOGIC ---


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    fields = ["title", "content"]
    template_name = "news_engine/submit_newsletter.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        if getattr(self.request.user, "role", "").lower() not in [
            "journalist",
            "editor",
        ]:
            messages.error(
                self.request, "Only Journalists and Editors can send newsletters."
            )
            return redirect("home")

        newsletter = form.save(commit=False)
        newsletter.creator = self.request.user
        newsletter.save()

        # --- READER EMAIL NOTIFICATION LOGIC ---
        subscribers = Subscription.objects.filter(
            journalist=self.request.user
        ).values_list("reader__email", flat=True)

        print(f"DEBUG: Newsletter Created: {newsletter.title}")
        print(f"DEBUG: Subscriber count: {len(subscribers)}")
        print(f"DEBUG: Recipient List: {list(subscribers)}")

        if subscribers:
            try:
                send_mail(
                    subject=f"New Newsletter: {newsletter.title}",
                    message=newsletter.content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(subscribers),
                    fail_silently=False,
                )
                print("DEBUG: Email sent successfully.")
            except Exception as e:
                print(f"DEBUG: Email failed: {str(e)}")
        else:
            print("DEBUG: No emails sent because the subscriber list is empty.")

        messages.success(self.request, "Newsletter published and emails queued!")
        return redirect(self.success_url)


class NewsletterUpdateView(LoginRequiredMixin, ContentAccessMixin, UpdateView):
    model = Newsletter
    fields = ["title", "content"]
    template_name = "news_engine/submit_newsletter.html"
    success_url = reverse_lazy("home")


class NewsletterDeleteView(LoginRequiredMixin, ContentAccessMixin, DeleteView):
    model = Newsletter
    template_name = "news_engine/newsletter_confirm_delete.html"
    success_url = reverse_lazy("home")


# --- EDITOR DASHBOARD ---


@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    """
    This method will be used to retrieve and display all pending articles and newsletters
    that require editorial review.

    :param HttpRequest request: The object representing the current HTTP request

    :returns: A rendered HTML page containing the editor's dashboard
    :rtype: HttpResponse
    """
    pending_articles = Article.objects.filter(is_approved=False).order_by("-created_at")
    all_newsletters = Newsletter.objects.all().order_by("-created_at")
    return render(
        request,
        "news_engine/editor_dashboard.html",
        {"pending_articles": pending_articles, "newsletters": all_newsletters},
    )


@login_required
@user_passes_test(is_editor)
def approve_article_html(request, article_id):
    """
    This method will be used to approve an article, mark it as live, and post a
    notification to X (Twitter).

    :param HttpRequest request: The object representing the current HTTP request
    :param int article_id: The unique identifier of the article to be approved

    :returns: A redirect to the editor dashboard
    :rtype: HttpResponseRedirect
    """
    article = get_object_or_404(Article, id=article_id)
    article.is_approved = True
    article.save()
    try:
        article.post_to_twitter()
        messages.success(request, f"Article '{article.title}' is live and posted to X!")
    except Exception as e:
        messages.warning(request, f"Article live, but X posting failed: {str(e)}")
    return redirect("editor_dashboard")


@login_required
@user_passes_test(is_editor)
def reject_article_html(request, article_id):
    """
    This method will be used to permanently delete an article from the database
    when it is rejected by an editor.

    :param HttpRequest request: The object representing the current HTTP request
    :param int article_id: The unique identifier of the article to be rejected

    :returns: A redirect to the editor dashboard
    :rtype: HttpResponseRedirect
    """
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    messages.warning(request, "Article rejected.")
    return redirect("editor_dashboard")


# --- SOCIAL ACTIONS ---


@login_required
def user_feed(request):
    following_ids = Subscription.objects.filter(reader=request.user).values_list(
        "journalist_id", flat=True
    )
    articles = Article.objects.filter(
        author_id__in=following_ids, is_approved=True
    ).order_by("-created_at")
    return render(request, "news_engine/user_feed.html", {"articles": articles})


def journalist_detail(request, pk):
    journalist = get_object_or_404(User, pk=pk)
    articles = Article.objects.filter(author=journalist, is_approved=True)
    followed = False
    if request.user.is_authenticated:
        followed = Subscription.objects.filter(
            reader=request.user, journalist=journalist
        ).exists()
    return render(
        request,
        "news_engine/journalist_detail.html",
        {"journalist": journalist, "articles": articles, "followed": followed},
    )


@login_required
def subscribe(request, target_type, target_id):
    if target_type == "journalist":
        target = get_object_or_404(User, id=target_id)
        sub, created = Subscription.objects.get_or_create(
            reader=request.user, journalist=target
        )
    elif target_type == "publisher":
        target = get_object_or_404(Publisher, id=target_id)
        sub, created = Subscription.objects.get_or_create(
            reader=request.user, publisher=target
        )
    else:
        return redirect("article_list")

    if not created:
        sub.delete()
        messages.info(request, "Subscription removed.")
    else:
        messages.success(request, "Subscription added!")
    return redirect(request.META.get("HTTP_REFERER", "article_list"))


# --- REST API ---


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.get_or_create(user=user)


class ArticleListCreate(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["title", "content"]

    def get_queryset(self):
        return Article.objects.filter(is_approved=True).order_by("-created_at")

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", "").lower() == "reader":
            raise exceptions.PermissionDenied("Readers cannot create articles.")
        serializer.save(author=self.request.user)


class UserFeedAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        following_ids = Subscription.objects.filter(
            reader=self.request.user
        ).values_list("journalist_id", flat=True)
        return Article.objects.filter(
            author_id__in=following_ids, is_approved=True
        ).order_by("-created_at")


class LikeArticleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, article=article)
        if not created:
            like.delete()
            return Response({"message": "Unliked"}, status=status.HTTP_200_OK)
        return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)
