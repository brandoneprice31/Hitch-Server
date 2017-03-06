from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from .users.urls import user_urls
from .drives.urls import drive_urls
from .hitches.urls import hitch_urls


urlpatterns = [
    url(r'^api-token-auth/', views.obtain_auth_token)
]

urlpatterns += user_urls
urlpatterns += drive_urls
urlpatterns += hitch_urls

urlpatterns = format_suffix_patterns(urlpatterns)
