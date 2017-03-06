from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .controller import *

hitch_urls = [
    url(r'^hitches/all/$', hitch_list)
]
