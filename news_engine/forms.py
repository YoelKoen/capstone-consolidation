from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Comment, Publisher

User = get_user_model()


# --- 1. User Registration ---
class CustomUserCreationForm(UserCreationForm):
    """Handles registration and ensures the 'role' and 'publisher' fields are saved."""

    class Meta(UserCreationForm.Meta):
        model = User

        fields = UserCreationForm.Meta.fields + ("email", "role", "publisher")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})

        if "publisher" in self.fields:
            self.fields["publisher"].label = (
                "Journalist Affiliation (Optional/Publisher House)"
            )


# --- 2. Article Submission ---
class ArticleSubmissionForm(forms.ModelForm):
    """The form journalists use to submit news for editor review."""

    class Meta:
        model = Article
        fields = ["title", "content", "category", "image"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a catchy headline",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Write your story here...",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


# --- 3. Comments ---
class CommentForm(forms.ModelForm):
    """Simple form for readers to engage with articles."""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Share your thoughts...",
                }
            ),
        }
        labels = {
            "content": "",
        }
