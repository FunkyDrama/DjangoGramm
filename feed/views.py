from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import Profile
from posts.models import Post
from .models import Follower
class FollowView(LoginRequiredMixin, View):
    """
    Handle POST to follow a user.
    """
    def post(self, request, username):
        me = request.user.profile
        target = get_object_or_404(Profile, user__username=username)
        if me != target:
            Follower.objects.get_or_create(follower=me, following=target)
        return redirect('profile_detail', username=username)


class UnfollowView(LoginRequiredMixin, View):
    """
    Handle POST to unfollow a user.
    """
    def post(self, request, username):
        me = request.user.profile
        target = get_object_or_404(Profile, user__username=username)
        Follower.objects.filter(follower=me, following=target).delete()
        return redirect('profile_detail', username=username)


class FollowingFeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed/following_feed.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        me = self.request.user.profile
        qs = (
            Post.objects
                .filter(author__followers__follower=me)
                .prefetch_related('images')
                .distinct()
        )
        return qs