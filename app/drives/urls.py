from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .controller import *

drive_urls = [
    url(r'^drives/all/$', user_drive_list),
    url(r'^drives/detail/$', user_drive_detail),
    url(r'^drives/search/$', drive_search)
]
