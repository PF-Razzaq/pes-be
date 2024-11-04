# Generated by Django 5.0.4 on 2024-04-25 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pes', '0004_merge_20240425_1257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='admin', max_length=255, unique=True),
        ),
    ]
