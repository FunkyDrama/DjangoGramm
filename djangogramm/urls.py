from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from posts.views import AllPostsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("posts/", include("posts.urls")),
    path("", AllPostsView.as_view(), name="main")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
