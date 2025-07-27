from django.contrib.auth import views as auth_views
from django.urls import path
from .views import RegisterView, VerifyEmailView, CompleteProfileView, HomeView

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="registration/logged_out.html"),
        name="logout",
    ),
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("complete-profile/", CompleteProfileView.as_view(), name="complete_profile"),
    path("", HomeView.as_view(), name="home"),
]
