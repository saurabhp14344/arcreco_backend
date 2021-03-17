from django.db import models
from django.conf import settings


class ContactUs(models.Model):
    """creating contact us table for user query"""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=12, blank=True, null=True)
    subject = models.CharField(max_length=160, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)

    def __str__(self):
        """string representation"""
        return self.subject

    class Meta:
        """model display name"""
        verbose_name_plural = "inquiries"