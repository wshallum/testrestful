from django.db import models


class Entry(models.Model):
    name = models.CharField(max_length=200)


class Phone(models.Model):
    type = models.CharField(max_length=20)
    number = models.CharField(max_length=50)
    parent = models.ForeignKey(Entry, related_name='phones')
