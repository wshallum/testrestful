from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^entries$', views.entries),
    url(r'^entries/(?P<id>\w+)$', views.entry, name='entry'),
]
