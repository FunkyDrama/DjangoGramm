# posts/views.py
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import Profile
from .models import Post, Image
from .forms import PostForm


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    template_name = "posts/create.html"

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        post = form.save(commit=False)

        profile = Profile.objects.get(user=self.request.user)
        post.author = profile
        post.save()

        for uploaded in self.request.FILES.getlist("images"):
            Image.objects.create(post=post, image=uploaded)

        return redirect(self.get_success_url())
