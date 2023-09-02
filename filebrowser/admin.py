from django.contrib import admin
from django.db import models

class browse(models.Model):
    class Meta:
        verbose_name_plural = "browse"

admin.site.register(browse)
