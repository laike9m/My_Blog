from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url('^$', views.home),
    url(r'^(?P<slug>[-\w\d]+),(?P<id>\d+)/$', views.blogpost),
    url('^archive/$', views.archive),
    url('^about/$', views.about),
    url('^projects/$', views.projects),
    url('^contact/$', views.contact),
)
