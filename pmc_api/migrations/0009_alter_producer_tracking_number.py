# Generated by Django 5.1.3 on 2024-11-26 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0008_producer_is_carry_bags_producer_is_plastic_packing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producer',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
