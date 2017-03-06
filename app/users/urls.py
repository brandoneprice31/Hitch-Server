from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .controller import *

user_urls = [
    url(r'^users/$', list_all),
    url(r'^users/create/$', create),
    url(r'^users/check/$', check_user),
    url(r'^users/login/$', login),
    url(r'^users/detail/$', detail),
    url(r'^users/delete/$', delete),
    url(r'^users/log-out/$', log_out)
]
