from django.db import models
from easy_thumbnails.files import get_thumbnailer

from accounts.models import Profile


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    caption = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return f"{self.author.user.username} - {self.caption[:20]}"


class Image(models.Model):
    post = models.ForeignKey(Post, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="posts/images/")

    def get_preview_url(self):
        if not self.image:
            return ""
        options = {"size": (300, 300), "crop": True}
        thumb = get_thumbnailer(self.image).get_thumbnail(options)
        return thumb.url

    def __str__(self):
        return f"Image for {self.post.author.user.username} - {self.post.caption[:20]}"
