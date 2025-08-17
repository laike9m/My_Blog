from django.urls import include, re_path, path
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from css3two_blog.views import home

urlpatterns = [
    # css3two_blog
    re_path(r"^(?P<page>\d*)/$", home),
    re_path(r"^$", home),
    re_path(r"^blog/", include("css3two_blog.urls")),
    # admin
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "my_blog.views.handler404"
