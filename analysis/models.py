from django.db import models


class User(models.Model):
    userId = models.CharField(max_length=255, primary_key=True)
    userName = models.CharField(max_length=255)
    headImgUrl = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    class Meta:
        db_table = 'user'


class News(models.Model):
    newsId = models.AutoField('newsId', primary_key=True)
    writerName = models.CharField(max_length=255)
    type = models.IntegerField()
    title = models.CharField(max_length=255)
    introduction = models.CharField(max_length=255)
    imgUrl = models.CharField(max_length=255)
    context = models.TextField(max_length=255)
    createdAt = models.DateTimeField()
    class Meta:
        db_table = 'news'


class TransmitNews(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    introduction = models.CharField(max_length=255)
    writerName = models.CharField(max_length=255)
    viewerName = models.CharField(max_length=255)
    shareName = models.CharField(max_length=255)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    class Meta:
        db_table = 'transmit_news'