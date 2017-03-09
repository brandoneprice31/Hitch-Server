from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .controller import *

drive_urls = [
    url(r'^drives/$', list_all),
    url(r'^drives/detail/$', detail),
    url(r'^drives/search/$', search),
    url(r'^drives/create/$', create),
    url(r'^drives/delete/$', delete)
]
