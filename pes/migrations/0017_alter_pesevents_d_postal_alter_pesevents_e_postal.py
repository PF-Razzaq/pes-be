# Generated by Django 5.0.4 on 2024-05-30 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pes', '0016_alter_pesevents_contract_alter_pesevents_dignityplan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesevents',
            name='d_Postal',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Postal',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
