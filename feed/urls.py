from django.urls import path
from .views import FollowView, UnfollowView, FollowingFeedView

urlpatterns = [
    path("u/<str:username>/follow/", FollowView.as_view(), name="profile_follow"),
    path("u/<str:username>/unfollow/", UnfollowView.as_view(), name="profile_unfollow"),
    path("following/", FollowingFeedView.as_view(), name="following_feed"),
]
