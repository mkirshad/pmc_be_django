# Generated by Django 5.1.6 on 2025-05-30 10:53

import pmc_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0070_competitionregistration'),
    ]

    operations = [
        migrations.AddField(
            model_name='competitionregistration',
            name='photo_object',
            field=models.ImageField(blank=True, null=True, upload_to=pmc_api.models.upload_student_card),
        ),
    ]
