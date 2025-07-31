from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from .models import Tag
from posts.models import Post


class TagListView(ListView):
    model = Tag
    template_name = "tags/tag_list.html"
    context_object_name = "tags"


class TaggedListView(ListView):
    model = Post
    template_name = "tags/tagged_posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        raw_slug = self.kwargs["slug"]
        self.tag = get_object_or_404(Tag, slug__iexact=raw_slug)
        return Post.objects.filter(tags=self.tag).prefetch_related("images")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        return ctx
