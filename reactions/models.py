from django.db import models
from posts.models import Post
from accounts.models import Profile


class Like(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    is_dislike = models.BooleanField(default=False)

    class Meta:
        unique_together = ("profile", "post")
        verbose_name = "Like"
        verbose_name_plural = "Likes"

    def __str__(self):
        return f"{self.profile.user.username} liked {self.post.caption[:20]}"
