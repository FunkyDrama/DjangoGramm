from django.contrib.auth import get_user_model
from accounts.pipeline import set_unusable_password_if_social
from unittest.mock import MagicMock
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class SocialAuthPipelineTest(TestCase):
    """
    Test case class for testing social authentication password handling.

    This class is designed to test the behavior of a social authentication pipeline
    that determines whether to set an unusable password for a user based on the
    backend and user creation status.

    """

    def test_sets_unusable_password_for_new_social_user(self):
        user = User.objects.create(username="socialuser", email="s@example.com")
        user.set_password("testpass")
        user.save()

        backend = MagicMock()
        backend.name = "google-oauth2"
        set_unusable_password_if_social(backend, user=user, is_new=True)

        user.refresh_from_db()
        self.assertFalse(user.has_usable_password())

    def test_does_not_override_existing_password(self):
        user = User.objects.create_user(
            username="existing", email="e@example.com", password="pass"
        )
        backend = MagicMock()
        backend.name = "google-oauth2"

        set_unusable_password_if_social(backend, user=user, is_new=False)
        user.refresh_from_db()
        self.assertTrue(user.has_usable_password())

    def test_ignores_non_social_backends(self):
        user = User.objects.create(username="socialuser2", email="x@example.com")
        backend = MagicMock()
        backend.name = "some-other-backend"

        set_unusable_password_if_social(backend, user=user, is_new=True)
        user.refresh_from_db()
        self.assertTrue(user.has_usable_password())


class SocialLoginButtonTest(TestCase):
    """
    Unit test class to verify social login button references in the login page.

    This test class ensures that the login page correctly includes the required
    links and text for Google and GitHub social login options.

    :ivar client: Django test client instance to perform web requests for testing.
    :type client: Client
    """

    def setUp(self):
        self.client = Client()

    def test_login_page_contains_google_link(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("/social-auth/login/google-oauth2/", response.content.decode())
        self.assertIn("google-oauth2", response.content.decode())
        self.assertIn("Continue with Google", response.content.decode())

    def test_login_page_contains_github_link(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("/social-auth/login/github/", response.content.decode())
        self.assertIn("github", response.content.decode())
        self.assertIn("Continue with GitHub", response.content.decode())


class SocialAuthRedirectTest(TestCase):
    """
    Test suite for verifying social authentication redirect functionality.

    This class tests the redirect behavior of social authentication flows
    for various providers. Test cases ensure that the application correctly
    redirects to the appropriate provider's authentication endpoints.

    Each test case simulates a client request for the start of a social
    authentication flow and verifies the resulting HTTP response status code
    as well as the correctness of the redirect URL.

    :ivar client: A test client to simulate HTTP requests during testing.
    :type client: Client
    """

    def setUp(self):
        self.client = Client()

    def test_google_auth_redirect(self):
        response = self.client.get(
            reverse("social:begin", args=["google-oauth2"]), follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.google.com", response["Location"])

    def test_github_auth_redirect(self):
        response = self.client.get(
            reverse("social:begin", args=["github"]), follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("github.com", response["Location"])
