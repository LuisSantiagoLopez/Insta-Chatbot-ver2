from django.db import models
from django.contrib.auth.models import User


class Newstitles(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    newstitle = models.TextField(default="", null=True)


class Ideas(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    instagram_idea = models.TextField(primary_key=True)
    caption = models.TextField()
    illustration = models.TextField()
    News = models.TextField()
    chosen = models.BooleanField(default=False)
    used = models.BooleanField(default=False)


class Conversations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    output = models.TextField()


class Tokens(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    total_tokens = models.IntegerField()
    prompt_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
    total_images = models.IntegerField()
    total_searches = models.IntegerField()
    total_cost = models.FloatField()

    class Meta:
        db_table = "tokens"
