from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from accounts.models import Profile
from accounts.forms import LoginForm, RegisterForm, ProfileForm
from accounts.tokens import email_verification_token
from posts.models import Post


User = get_user_model()


class ProfileModelTest(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(
            username="u1", email="u1@example.com", password="pass"
        )
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_signal_only_on_create(self):
        user = User.objects.create_user("u2", email="u2@example.com", password="pass")
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        user.email = "new@ex.com"
        user.save()
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)

    def test_str_and_defaults(self):
        user = User.objects.create_user("u3", email="u3@example.com", password="pass")
        profile = Profile.objects.get(user=user)
        self.assertEqual(str(profile), "u3's Profile")
        self.assertEqual(profile.bio, "")
        self.assertFalse(profile.avatar)


class ProfileAdminTest(TestCase):
    def test_profile_admin_registered(self):
        self.assertIn(Profile, admin.site._registry)
        ma = admin.site._registry[Profile]
        self.assertEqual(ma.list_display, ("user", "bio"))
        self.assertEqual(ma.search_fields, ("user__username",))


class LoginFormTest(TestCase):
    def test_empty_form(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password", form.errors)

    def test_valid_data(self):
        form = LoginForm(data={"username": "u", "password": "p"})
        self.assertTrue(form.is_valid())


class RegisterFormTest(TestCase):
    def setUp(self):
        User.objects.create_user(username="exist", email="e@e.com", password="pass")

    def test_password_mismatch(self):
        form = RegisterForm(
            data={
                "email": "a@b.com",
                "password1": "p1",
                "password2": "p2",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertEqual(form.errors["__all__"][0], "Passwords do not match.")

    def test_duplicate_email(self):
        form = RegisterForm(
            data={
                "email": "e@e.com",
                "password1": "p",
                "password2": "p",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(form.errors["email"][0], "Email is already in use.")

    def test_valid_data(self):
        form = RegisterForm(
            data={
                "email": "new@e.com",
                "password1": "p",
                "password2": "p",
            }
        )
        self.assertTrue(form.is_valid())


class ProfileFormTest(TestCase):
    def test_clean_username_required(self):
        form = ProfileForm(
            data={
                "username": "",
                "first_name": "F",
                "last_name": "L",
            }
        )
        self.assertFalse(form.is_valid())
        # Пустой username — стандартная ошибка required
        self.assertEqual(form.errors["username"][0], "This field is required.")

    def test_missing_required_fields(self):
        form = ProfileForm(data={"username": "u"})
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)

    def test_valid_data(self):
        form = ProfileForm(
            data={
                "username": "u",
                "first_name": "First",
                "last_name": "Last",
                "bio": "Hello",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], "u")
        self.assertEqual(form.cleaned_data["bio"], "Hello")


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_register(self):
        resp = self.client.get(reverse("register"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/register.html")
        self.assertIsInstance(resp.context["form"], RegisterForm)

    def test_post_invalid(self):
        resp = self.client.post(
            reverse("register"), {"email": "x", "password1": "a", "password2": "b"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/register.html")
        self.assertFalse(resp.context["form"].is_valid())

    def test_post_valid_creates_user_and_sends_email(self):
        resp = self.client.post(
            reverse("register"),
            {
                "email": "y@e.com",
                "password1": "pass123",
                "password2": "pass123",
            },
        )
        user = User.objects.get(email="y@e.com")
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Account Verification", mail.outbox[0].subject)
        self.assertTemplateUsed(resp, "registration/email_verify.html")


class VerifyEmailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "v@v.com", "v@v.com", "pass", is_active=False
        )
        self.client = Client()

    def test_verify_success(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = email_verification_token.make_token(self.user)
        resp = self.client.get(
            reverse("verify_email", kwargs={"uidb64": uid, "token": token})
        )
        self.assertRedirects(resp, reverse("complete_profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verify_invalid_uid(self):
        resp = self.client.get(
            reverse("verify_email", kwargs={"uidb64": "bad", "token": "bad"})
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid verification link.", resp.content.decode())

    def test_verify_wrong_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        resp = self.client.get(
            reverse("verify_email", kwargs={"uidb64": uid, "token": "wrong"})
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Email verification failed.", resp.content.decode())


class CompleteProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            "c@c.com", "c@c.com", "pass", is_active=True
        )

    def test_login_required(self):
        url = reverse("complete_profile")
        resp = self.client.get(url)
        self.assertRedirects(resp, f"{reverse('login')}?next={url}")

    def test_get_form(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("complete_profile"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/complete_profile.html")
        form = resp.context["form"]
        self.assertTrue(hasattr(form, "initial"))
        self.assertEqual(form.initial.get("username"), "Enter your username here")

    def test_post_valid_updates_profile(self):
        self.client.force_login(self.user)
        data = {
            "username": "newname",
            "first_name": "First",
            "last_name": "Last",
            "bio": "Bio here",
        }
        resp = self.client.post(reverse("complete_profile"), data)
        self.assertRedirects(resp, reverse("home"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newname")
        self.assertEqual(self.user.first_name, "First")
        self.assertEqual(self.user.last_name, "Last")
        self.assertEqual(self.user.profile.bio, "Bio here")

    def test_post_invalid_shows_errors(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("complete_profile"), {"username": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context["form"].is_valid())


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create_user("u1", "u1@x.com", "pass")
        Profile.objects.get(user=self.u1)
        Post.objects.create(author=self.u1.profile, caption="one")
        Post.objects.create(author=self.u1.profile, caption="two")

        self.u2 = User.objects.create_user("u2", "u2@x.com", "pass")
        Profile.objects.get(user=self.u2)
        Post.objects.create(author=self.u2.profile, caption="other")

    def test_login_required(self):
        resp = self.client.get(reverse("home"))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('home')}")

    def test_home_shows_only_own_posts(self):
        self.client.force_login(self.u1)
        resp = self.client.get(reverse("home"))
        captions = {p.caption for p in resp.context["posts"]}
        self.assertEqual(captions, {"one", "two"})
