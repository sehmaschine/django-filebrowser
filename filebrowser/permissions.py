from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class FileBrowserPermissionManager(models.Manager):
    def get_queryset(self):
        return super(FileBrowserPermissionManager, self).\
            get_queryset().filter(content_type__name='filebrowser_permission')


class FileBrowserPermission(Permission):
    """Permission for the file browser, not attached to a model"""

    objects = FileBrowserPermissionManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        ct, created = ContentType.objects.get_or_create(
            name="filebrowser", app_label=self._meta.app_label
        )
        self.content_type = ct
        super(FileBrowserPermission, self).save(*args, **kwargs)
