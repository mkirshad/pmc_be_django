# Generated by Django 5.1.3 on 2024-11-25 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0006_alter_businessprofile_city_town_village_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessprofile',
            name='district',
        ),
        migrations.RemoveField(
            model_name='businessprofile',
            name='tehsil',
        ),
    ]
