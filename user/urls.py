from django.urls import path
from django.conf.urls import include, url
from . import views
from user.views import *
from user.search import *


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search-form/$', search_form),
    url(r'^search/$', search),
]
