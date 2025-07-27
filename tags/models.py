from django.db import models

from posts.models import Post


class Tag(models.Model):
    post = models.ManyToManyField(Post, related_name="tags", blank=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]
