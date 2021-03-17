from django.db import models
from django.conf import settings
from django.utils.timezone import now


class UploadFiles(models.Model):
    """csv or excel files uploaded by users"""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, blank=True, null=True)
    file = models.FileField(blank=True, null=True)
    type = models.CharField(max_length=60, blank=True, null=True)
    created_date = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        """string representation"""
        return self.name

    class Meta:
        """model display name"""
        verbose_name_plural = "Upload files"

