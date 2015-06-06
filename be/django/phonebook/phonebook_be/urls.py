from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^entries$', views.entries),
    url(r'^entries/(?P<id>\w+)$', views.entry, name='entry'),
    url(r'^entries/(?P<entry_id>\w+)/(?P<id>\w+)$', views.phone, name='phone'),
]
