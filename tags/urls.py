# tags/urls.py
from django.urls import path
from .views import TagListView, TaggedListView

urlpatterns = [
    path("", TagListView.as_view(), name="tag_list"),
    path("<slug:slug>/", TaggedListView.as_view(), name="tagged_posts"),
]
