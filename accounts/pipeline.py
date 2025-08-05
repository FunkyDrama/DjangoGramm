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
