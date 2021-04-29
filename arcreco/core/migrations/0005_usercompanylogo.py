# Generated by Django 2.2 on 2021-04-28 11:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210428_1145'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCompanyLogo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_logo', models.ImageField(upload_to='images/profile/')),
                ('users', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
