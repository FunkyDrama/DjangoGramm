from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, ListView
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


class AllPostsView(ListView):
    model = Post
    template_name = "main.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        return (
            super().get_queryset().select_related("author").prefetch_related("images")
        )

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        if request.headers.get("x-requested-with") == "XMLHttpRequest":

            return render(request, "posts/posts_list.html", context)

        return super().get(request, *args, **kwargs)
