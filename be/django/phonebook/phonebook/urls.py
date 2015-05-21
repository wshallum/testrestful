from django.conf.urls import include, url
from django.contrib import admin
import phonebook_be.urls

urlpatterns = [
    # Examples:
    # url(r'^$', 'phonebook.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', include(phonebook_be.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
