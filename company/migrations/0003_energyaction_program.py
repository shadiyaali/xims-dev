# Generated by Django 5.1.4 on 2025-01-02 05:47

import company.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_energyimprovement'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnergyAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_plan', models.CharField(blank=True, max_length=50, null=True)),
                ('associative_objective', models.CharField(blank=True, max_length=50, null=True)),
                ('legal_requirements', models.CharField(blank=True, max_length=50, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('energy_improvements', models.TextField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('upload_attachment', models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit)),
                ('means', models.CharField(blank=True, max_length=50, null=True)),
                ('statement', models.TextField(blank=True, null=True)),
                ('responsible', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_energy_action_plan', to='company.users')),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Program', models.CharField(blank=True, max_length=50, null=True)),
                ('energy_action', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progarms', to='company.energyaction')),
            ],
        ),
    ]
