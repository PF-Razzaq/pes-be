# Generated by Django 5.0.4 on 2024-07-19 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pes', '0028_pesfulldump'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aftercare',
            fields=[
                ('EventID', models.BigIntegerField(db_column='EventID', primary_key=True, serialize=False)),
                ('d_First', models.CharField(blank=True, db_column='d_First', max_length=75, null=True)),
                ('d_Last', models.CharField(blank=True, db_column='d_Last', max_length=125, null=True)),
                ('e_Last', models.CharField(blank=True, db_column='e_Last', max_length=125, null=True)),
                ('Status', models.CharField(blank=True, db_column='Status', max_length=50, null=True)),
                ('eventdate', models.DateTimeField(blank=True, null=True)),
                ('locationid', models.IntegerField(db_column='LocationID')),
            ],
            options={
                'db_table': 'Aftercare',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Aftercare360',
            fields=[
                ('EventID', models.BigIntegerField(db_column='EventID', primary_key=True, serialize=False)),
                ('d_First', models.CharField(blank=True, db_column='d_First', max_length=75, null=True)),
                ('d_Last', models.CharField(blank=True, db_column='d_Last', max_length=125, null=True)),
                ('e_Last', models.CharField(blank=True, db_column='e_Last', max_length=125, null=True)),
                ('Status', models.CharField(blank=True, db_column='Status', max_length=50, null=True)),
                ('eventdate', models.DateTimeField(blank=True, null=True)),
                ('locationid', models.IntegerField(db_column='LocationID')),
            ],
            options={
                'db_table': 'Aftercare360',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('alpha2', models.CharField(blank=True, max_length=50, null=True)),
                ('alpha3', models.CharField(blank=True, max_length=50, null=True)),
                ('countrycode', models.IntegerField(blank=True, null=True)),
                ('iso', models.CharField(blank=True, max_length=50, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('subregion', models.CharField(blank=True, max_length=100, null=True)),
                ('intermediateregion', models.CharField(blank=True, max_length=100, null=True)),
                ('regioncode', models.IntegerField(blank=True, null=True)),
                ('subregioncode', models.IntegerField(blank=True, null=True)),
                ('intermediateregioncode', models.IntegerField(blank=True, null=True)),
                ('isactive', models.IntegerField()),
                ('orderby', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'country',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Modifier',
            fields=[
                ('EventID', models.BigIntegerField(db_column='EventID', primary_key=True, serialize=False)),
                ('d_First', models.CharField(blank=True, db_column='d_First', max_length=75, null=True)),
                ('d_Last', models.CharField(blank=True, db_column='d_Last', max_length=125, null=True)),
                ('e_Last', models.CharField(blank=True, db_column='e_Last', max_length=125, null=True)),
                ('Status', models.CharField(blank=True, db_column='Status', max_length=50, null=True)),
                ('eventdate', models.DateTimeField(blank=True, null=True)),
                ('locationid', models.IntegerField(db_column='LocationID')),
            ],
            options={
                'db_table': 'Modifier',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='pesevents',
            name='d_Country',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
        migrations.AddField(
            model_name='pesevents',
            name='e_Country',
            field=models.CharField(blank=True, max_length=125, null=True),
        ),
    ]
