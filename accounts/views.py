from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import DetailView

from accounts.forms import RegisterForm, ProfileForm
from accounts.models import Profile
from accounts.tokens import email_verification_token
from feed.models import Follower
from posts.models import Post


class RegisterView(View):

    @staticmethod
    def _send_verification(user, request):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse("verify_email", kwargs={"uidb64": uid, "token": token})
        )
        send_mail(
            subject="Account Verification",
            message=f"Click this link to activate account: {activation_link}",
            recipient_list=[user.email],
            from_email=None,
        )
        return activation_link

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, "registration/register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password1"]
            existing = User.objects.filter(email__iexact=email).first()
            if existing:
                if not existing.is_active:
                    self._send_verification(existing, request)
                    messages.info(
                        request, "Verification email resent. Please check your inbox."
                    )
                    return render(
                        request, "registration/email_verify.html", {"resent": True}
                    )
                else:
                    form.add_error("email", "Email is already in use.")
                    return render(request, "registration/register.html", {"form": form})

            user = User.objects.create_user(
                username=email, email=email, password=password, is_active=False
            )
            self._send_verification(user, request)
            return render(request, "registration/email_verify.html")

        return render(request, "registration/register.html", {"form": form})


class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            if email_verification_token.check_token(user, token):
                user.is_active = True
                user.save()
                login(request, user)
                return redirect("complete_profile")
            else:
                return HttpResponse("Email verification failed.", status=400)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse("Invalid verification link.", status=400)


@method_decorator(login_required, name="dispatch")
class CompleteProfileView(View):
    form_class = ProfileForm
    template_name = "registration/complete_profile.html"

    def get(self, request):
        form = self.form_class(
            initial={
                "username": "",
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "bio": getattr(request.user.profile, "bio", ""),
            }
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.profile.bio = form.cleaned_data["bio"]
            if form.cleaned_data.get("avatar"):
                user.profile.avatar = form.cleaned_data["avatar"]
            user.save()
            user.profile.save()
            return redirect("home")
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class HomeView(View):

    def get(self, request):
        profile = request.user.profile
        posts = Post.objects.filter(author=profile).prefetch_related("images")
        return render(
            request,
            "accounts/user/home.html",
            {
                "user": request.user,
                "posts": posts,
            },
        )


class ProfileDetailView(LoginRequiredMixin, DetailView):
    def get(self, request, username):
        target = get_object_or_404(Profile, user__username=username)
        posts = Post.objects.filter(author=target).prefetch_related("images")

        is_following = False
        if request.user.is_authenticated:
            me = request.user.profile
            is_following = Follower.objects.filter(
                follower=me, following=target
            ).exists()

        return render(
            request,
            "accounts/user/profile_detail.html",
            {
                "target_profile": target,
                "posts": posts,
                "is_following": is_following,
            },
        )
