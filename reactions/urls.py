from django.urls import path
from .views import ReactionView

urlpatterns = [
    path("posts/<int:post_id>/react/", ReactionView.as_view(), name="post_react"),
]
