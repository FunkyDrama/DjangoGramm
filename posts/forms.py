from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["caption"]
        widgets = {
            "caption": forms.Textarea(
                attrs={
                    "class": (
                        "border rounded px-3 py-2 border-gray-300 focus:border-blue-500 "
                        "focus:ring-2 focus:ring-blue-300 dark:border-gray-600 "
                        "dark:focus:border-white dark:focus:ring-white/50 bg-white "
                        "dark:bg-gray-800 text-gray-900 dark:text-gray-100 "
                        "transition-colors duration-150"
                    ),
                    "rows": 4,
                }
            ),
        }
