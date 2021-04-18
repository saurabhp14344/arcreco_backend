from django.contrib import admin
from .models import UploadFiles, TotalReconcile


class UserUploadFiles(admin.ModelAdmin):
    list_display = ('name', 'file', 'type', 'created_date')


class UserTotalReconcile(admin.ModelAdmin):
    list_display = ('name', 'sales_count', 'reconcile_count')


admin.site.register(UploadFiles, UserUploadFiles)
admin.site.register(TotalReconcile, UserTotalReconcile)
