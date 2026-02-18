from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["caption"]
        widgets = {
            "caption": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Write a caption… (optional)"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["caption"].required = False
