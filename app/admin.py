from django.contrib import admin
from .profiles.model import Profile
from .drives.model import Drive
from .hitches.model import Hitch

# Register your models here.
admin.site.register(Profile)
admin.site.register(Drive)
admin.site.register(Hitch)
