from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse
from django.views.generic import ListView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import Profile
from posts.models import Post
from .models import Follower


class FollowView(LoginRequiredMixin, RedirectView):
    def post(self, request, username, *args, **kwargs):
        me = request.user.profile
        target = get_object_or_404(Profile, user__username=username)
        if me != target:
            Follower.objects.get_or_create(follower=me, following=target)
        self.username = username

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"is_following": True, "username": username})

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("profile_detail", kwargs={"username": self.username})


class UnfollowView(LoginRequiredMixin, RedirectView):
    def post(self, request, username, *args, **kwargs):
        me = request.user.profile
        target = get_object_or_404(Profile, user__username=username)
        Follower.objects.filter(follower=me, following=target).delete()
        self.username = username

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"is_following": False, "username": username})

        return super().post(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse("profile_detail", kwargs={"username": self.username})


class FollowingFeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "feed/following_feed.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        me = self.request.user.profile
        qs = (
            Post.objects.filter(author__followers__follower=me)
            .prefetch_related("images")
            .distinct()
        )
        return qs
