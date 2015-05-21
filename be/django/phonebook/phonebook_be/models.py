from django.db import models


class Entry(models.Model):
    name = models.CharField(max_length=200)
