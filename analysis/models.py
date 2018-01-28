from django.db import models


class User(models.Model):
    userId = models.CharField(max_length=255)
    userName = models.CharField(max_length=255)
    headImgUrl = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)