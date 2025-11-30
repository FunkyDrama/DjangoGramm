import requests
from django.core.files.base import ContentFile


def set_unusable_password_if_social(backend, user=None, is_new=False, *args, **kwargs):
    """
    Sets an unusable password for a user if they registered through specific social backends.

    This function evaluates whether a newly registered user utilized a particular
    social backend for registration. If so, it sets an unusable password on the
    user account, meaning the user cannot authenticate using a password. Instead,
    other authentication mechanisms (e.g., social logins) are expected to be used.

    :param backend: The social backend object used during authentication.
    :param user: The user instance being evaluated, optional.
    :param is_new: A boolean indicating if the user is newly registered.
    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments.
    :return: None
    """
    social_backend_names = {"github", "google-oauth2", "google-oauth"}

    if is_new and backend.name in social_backend_names and user:
        user.set_unusable_password()
        user.save()


def save_profile_avatar(backend, user, response, *args, **kwargs):
    """
    Downloads and saves the user's profile picture from social authentication providers.

    Supports GitHub and Google OAuth2. Downloads the avatar image and saves it
    to the user's Profile model.

    :param backend: The social backend object used during authentication.
    :param user: The authenticated user instance.
    :param response: The response data from the social provider.
    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments.
    :return: None
    """
    if not user:
        return

    profile = getattr(user, "profile", None)
    if not profile:
        from accounts.models import Profile

        profile = Profile.objects.create(user=user)

    if profile.avatar:
        return

    avatar_url = None

    if backend.name == "github":
        avatar_url = response.get("avatar_url")

    elif backend.name == "google-oauth2":
        avatar_url = response.get("picture")

    if avatar_url:
        try:
            img_response = requests.get(avatar_url, timeout=10)
            if img_response.status_code == 200:
                file_name = f"{user.username}_avatar.jpg"
                profile.avatar.save(
                    file_name, ContentFile(img_response.content), save=True
                )
        except Exception as e:
            print(f"Failed to download avatar for {user.username}: {e}")
