# Generated by Django 5.0.4 on 2024-05-30 07:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pes', '0015_alter_pesevents_faxdate_alter_pesevents_reportdate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesevents',
            name='Contract',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='DignityPlan',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='ExecutorID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='FSPID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='FaxDate',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='OLDdID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='ReportDate',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='Status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_AreaCode',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_BCN',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_City',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_DOB',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_DOD',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_First',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Last',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Maiden',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_PHC',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Postal',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Prov',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Prov_PHC',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_SIN',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_Unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_birth_City',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_birth_Country',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_birth_Prov',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_death_City',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_death_Country',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_death_Prov',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_death_age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_disp_Postal',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_dispdate',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_exchange',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_middle_a',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_middle_b',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='d_phone',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_AreaCode',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_City',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_First',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Initial',
            field=models.CharField(blank=True, max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Last',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Postal',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Prov',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Salutation',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_Unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_exchange',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_phone_4',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='e_relationship',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='eventdate',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='pesevents',
            name='notes',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='pesexecutor',
            name='Password',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pesexecutor',
            name='Status',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pesexecutor',
            name='Username',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
