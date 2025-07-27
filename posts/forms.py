from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["caption"]
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 4}),
        }
