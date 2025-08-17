from django.urls import path, re_path
from . import views
from .feeds import BlogPostFeed

urlpatterns = [
    path("", views.home),
    re_path(r"^(?P<slug>[-\w\d]+),(?P<post_id>\d+)/$", views.blogpost, name="blogpost"),
    path("archive/", views.archive),
    path("about/", views.about),
    path("projects/", views.projects),
    path("talks/", views.talks),
    path("podcasts/", views.podcasts),
    re_path(r"^article/(?P<freshness>.*)/$", views.article),
    path("rss/", BlogPostFeed()),
]
