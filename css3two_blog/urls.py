from django.conf.urls import url,include
from . import views

urlpatterns = [
    url(r'^archive/$',views.archive,name='archive'),
    url(r'^(?P<slug>[-\w\d]+),(?P<blog_id>\d+)/$',views.blog,name='blog'),
    url(r'^archive/(?P<name>\w+)/$',views.archive,name='category'),
    url(r'^tag/(?P<name>\w+)/$',views.search_tag,name='tag'),
    url(r'^search/$',views.search_blog,name='search_blog'),
               ]