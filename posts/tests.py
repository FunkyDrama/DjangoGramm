from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest import mock

from accounts.models import Profile
from .models import Post, Image
from .forms import PostForm


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u1", email="u1@example.com", password="pass"
        )
        self.profile = Profile.objects.get(user=self.user)
        self.post = Post.objects.create(author=self.profile, caption="X" * 30)

    def test_str(self):
        expected = f"{self.user.username} - {self.post.caption[:20]}"
        self.assertEqual(str(self.post), expected)

    def test_default_ordering(self):
        p1 = Post.objects.create(author=self.profile, caption="first")
        p2 = Post.objects.create(author=self.profile, caption="second")
        qs = list(Post.objects.all())
        self.assertEqual(qs[0], p2)
        self.assertEqual(qs[1], p1)
        self.assertEqual(qs[2], self.post)


class ImageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u2", email="u2@example.com", password="pass"
        )
        self.profile = Profile.objects.get(user=self.user)
        self.post = Post.objects.create(author=self.profile, caption="cap")

    def test_get_preview_url_no_image(self):
        img = Image(post=self.post)
        self.assertEqual(img.get_preview_url(), "")

    @mock.patch("posts.models.get_thumbnailer")
    def test_get_preview_url_with_image(self, mock_get_thumb):
        dummy = SimpleUploadedFile("test.jpg", b"contents", content_type="image/jpeg")
        img = Image.objects.create(post=self.post, image=dummy)
        thumb_instance = mock_get_thumb.return_value
        thumb_instance.get_thumbnail.return_value.url = "/thumb.jpg"

        url = img.get_preview_url()
        mock_get_thumb.assert_called_with(img.image)
        self.assertEqual(url, "/thumb.jpg")


class AdminTest(TestCase):
    def test_post_admin_registration(self):
        self.assertIn(Post, admin.site._registry)
        ma = admin.site._registry[Post]
        self.assertEqual(ma.list_display, ("author", "caption"))
        self.assertEqual(ma.list_filter, ("author", "created"))
        self.assertEqual(ma.search_fields, ("caption", "author__user__username"))
        self.assertEqual(ma.date_hierarchy, "created")
        self.assertEqual(ma.ordering, ("-created",))


class FormTest(TestCase):
    def test_post_form_fields_and_widget(self):
        form = PostForm()
        self.assertIn("caption", form.fields)
        widget = form.fields["caption"].widget
        from django.forms import Textarea

        self.assertIsInstance(widget, Textarea)
        self.assertEqual(widget.attrs.get("rows"), 4)


class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="u3", email="u3@example.com", password="pass"
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_get_requires_login(self):
        url = reverse("post_create")
        resp = self.client.get(url)
        login_url = reverse("login")
        self.assertRedirects(resp, f"{login_url}?next={url}")

    def test_get_logged_in(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("post_create"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "posts/create.html")
        self.assertIn("form", resp.context)
        self.assertIsInstance(resp.context["form"], PostForm)

    def test_post_creates_post_and_images(self):
        self.client.force_login(self.user)
        url = reverse("post_create")

        f1 = SimpleUploadedFile("a.jpg", b"data1", content_type="image/jpeg")
        f2 = SimpleUploadedFile("b.jpg", b"data2", content_type="image/jpeg")

        resp = self.client.post(
            url,
            {
                "caption": "hello",
                "images": [f1, f2],
            },
        )
        self.assertEqual(resp.status_code, 302)

        post = Post.objects.get(caption="hello")
        self.assertEqual(post.author, self.profile)

        imgs = Image.objects.filter(post=post)
        self.assertEqual(imgs.count(), 2)
