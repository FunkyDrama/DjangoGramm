from django.db import models
from accounts.models import Profile


class Follower(models.Model):
    follower = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        verbose_name = "Follower"
        verbose_name_plural = "Followers"

    def __str__(self):
        return f"{self.follower.user.username} follows {self.following.user.username}"
