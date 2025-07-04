# Generated by Django 5.1.6 on 2025-02-25 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0063_districtplasticcommitteedocument_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='districtplasticcommitteedocument',
            name='document_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='districtplasticcommitteedocument',
            name='document_type',
            field=models.CharField(choices=[('Notification', 'Notification'), ('Minutes of Meeting', 'Minutes of Meeting')], max_length=50),
        ),
    ]
