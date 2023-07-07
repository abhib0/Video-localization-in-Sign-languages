from django.db import models
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
# Create your models here.



class MyModel(models.Model):
    file = models.FileField(upload_to='vids/')



