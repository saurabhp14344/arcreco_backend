# Generated by Django 2.2 on 2021-05-25 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recon', '0011_auto_20210430_0015'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadfiles',
            name='document',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
