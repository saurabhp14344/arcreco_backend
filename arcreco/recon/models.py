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


class TotalReconcile(models.Model):
    """Store informations about sales"""
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, blank=True, null=True)
    sales_count = models.IntegerField()
    reconcile_count = models.IntegerField()
    ageing_count = models.IntegerField()
    start_date = models.DateTimeField(null=True, editable=False)
    end_date = models.DateTimeField(null=True, editable=False)
    created_date = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        """string representation"""
        return self.name

    class Meta:
        """model display name"""
        verbose_name_plural = "Total Reconcile Data"
