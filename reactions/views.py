from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from posts.models import Post
from .models import Like


class ReactionView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        profile = request.user.profile
        reaction = request.POST.get("reaction")
        is_dislike = reaction == "dislike"

        obj, created = Like.objects.get_or_create(
            post=post, profile=profile, defaults={"is_dislike": is_dislike}
        )
        if not created:
            if obj.is_dislike == is_dislike:
                obj.delete()
            else:
                obj.is_dislike = is_dislike
                obj.save()

        next_url = request.POST.get("next")
        if not next_url:
            next_url = request.META.get("HTTP_REFERER")
        if not next_url:
            next_url = reverse("feed")

        return redirect(next_url)
