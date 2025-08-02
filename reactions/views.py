from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from posts.models import Post
from reactions.models import Like


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
                action = "removed"
            else:
                obj.is_dislike = is_dislike
                obj.save()
                action = "switched"
        else:
            action = "added"

        likes = post.likes.filter(is_dislike=False).count()
        dislikes = post.likes.filter(is_dislike=True).count()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "likes": likes,
                    "dislikes": dislikes,
                    "action": action,
                }
            )

        next_url = (
            request.POST.get("next")
            or request.META.get("HTTP_REFERER")
            or reverse("feed")
        )
        return redirect(next_url)
