from django.db import models
from django.contrib.auth.models import User

class ZKPProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # This stores 'y' from the ZKP algorithm
    public_key = models.CharField(max_length=255) 

    def __str__(self):
        return f"ZKP Profile for {self.user.username}"