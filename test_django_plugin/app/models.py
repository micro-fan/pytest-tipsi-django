from django.db import models

# Create your models here.


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Book(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
