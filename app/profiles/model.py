from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.BinaryField()

    def __str__ (self):
        return self.user.first_name + " " + self.user.last_name

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
            instance.profile.save()

    @receiver(post_save, sender=User)
    def create_auth_token(sender,instance=None,created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)
