# Generated by Django 5.1.6 on 2025-04-14 10:34

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pmc_api', '0064_districtplasticcommitteedocument_document_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DistrictsNew',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('short_name', models.CharField(blank=True, max_length=50, null=True)),
                ('division_name', models.CharField(blank=True, max_length=50, null=True)),
                ('district_id', models.IntegerField(blank=True, null=True)),
                ('division_id', models.IntegerField(blank=True, null=True)),
                ('extent', models.CharField(blank=True, max_length=100, null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                'db_table': 'districts_new',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EecClubs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emiscode', models.IntegerField(blank=True, null=True)),
                ('school_name', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('head_name', models.CharField(blank=True, max_length=255, null=True)),
                ('head_mobile_no_field', models.CharField(blank=True, db_column='head_mobile_no  ', max_length=255, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Boys', 'Boys'), ('Girls', 'Girls')], max_length=255, null=True)),
                ('education_level', models.CharField(blank=True, choices=[('Primary', 'Primary'), ('Middle', 'Middle'), ('High School', 'High School'), ('High. Sec', 'High. Sec')], max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('added_by', models.CharField(blank=True, max_length=255, null=True)),
                ('district_name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('notification_path', models.FileField(blank=True, null=True, upload_to='eec_notification', verbose_name='Notification')),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                'db_table': 'eec_clubs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('login', 'Login'), ('logout', 'Logout')], max_length=10)),
                ('model_name', models.CharField(blank=True, max_length=255, null=True)),
                ('object_id', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
