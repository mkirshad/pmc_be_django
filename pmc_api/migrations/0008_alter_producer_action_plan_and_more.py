# Generated by Django 5.1.3 on 2024-12-07 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0007_remove_businessprofile_district_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producer',
            name='action_plan',
            field=models.FileField(blank=True, null=True, upload_to='media/action_plan/'),
        ),
        migrations.AlterField(
            model_name='producer',
            name='consent_permit',
            field=models.FileField(blank=True, null=True, upload_to='media/permit/'),
        ),
        migrations.AlterField(
            model_name='producer',
            name='flow_diagram',
            field=models.FileField(blank=True, null=True, upload_to='media/diagrams/'),
        ),
        migrations.AlterField(
            model_name='producer',
            name='personnel_or_consumers_list',
            field=models.FileField(blank=True, null=True, upload_to='media/consumers/'),
        ),
        migrations.AlterField(
            model_name='recycler',
            name='registration_certificate',
            field=models.FileField(blank=True, null=True, upload_to='media/labor_dept/'),
        ),
    ]
