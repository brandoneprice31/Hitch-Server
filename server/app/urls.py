from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .users.controller import user_list, user_detail, log_out
from .drives.controller import user_drive_list, user_drive_detail
from rest_framework.authtoken import views


urlpatterns = [
    url(r'^users/$', user_list),
    url(r'^users/(?P<pk>[0-9]+)$', user_detail),
    url(r'^get-users-token/$', views.obtain_auth_token),
    url(r'^log-out/$', log_out),
    url(r'^user-drives/$' ,user_drive_list),
    url(r'^user-drives/(?P<pk>[0-9]+)$', user_drive_detail)
]

urlpatterns = format_suffix_patterns(urlpatterns)
