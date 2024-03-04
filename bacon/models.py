from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    players = models.TextField()

    def __str__(self):
        return f"{self.user}: {self.score}, {self.players}"