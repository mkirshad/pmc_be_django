# Generated by Django 5.1.3 on 2024-12-09 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0019_alter_producer_tracking_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producer',
            name='has_waste_storage_capacity',
            field=models.CharField(blank=True, choices=[('Available', 'Available'), ('Not Available', 'Not Available')], max_length=255, null=True),
        ),
    ]
