# Generated by Django 2.2 on 2021-02-16 12:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recon', '0003_auto_20210215_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadfiles',
            name='created_date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
