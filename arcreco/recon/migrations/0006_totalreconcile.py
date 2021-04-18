# Generated by Django 2.2 on 2021-04-16 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recon', '0005_uploadfiles_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='TotalReconcile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=60, null=True)),
                ('sales_count', models.IntegerField()),
                ('reconcile_count', models.IntegerField()),
                ('ageing_count', models.IntegerField()),
                ('start_date', models.DateTimeField(editable=False, null=True)),
                ('end_date', models.DateTimeField(editable=False, null=True)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Total Reconcile Data',
            },
        ),
    ]