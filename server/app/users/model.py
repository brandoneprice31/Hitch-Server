from django.db import models

# Create your models here.
class User(models.Model):

    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    profileImage = models.ImageField(upload_to='profile_images/',blank=True)


    def __str__ (self):
        return self.firstName + " " + self.lastName
