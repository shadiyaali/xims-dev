# Generated by Django 5.1.4 on 2025-01-02 07:05

import company.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_objectives'),
    ]

    operations = [
        migrations.CreateModel(
            name='TargetsP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.CharField(blank=True, max_length=50, null=True)),
                ('associative_objective', models.CharField(blank=True, max_length=50, null=True)),
                ('target_date', models.DateField(blank=True, null=True)),
                ('reminder_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('On Going', 'On Going'), ('Achieved', 'Achieved'), ('Not Achieved', 'Not Achieved'), ('Modified', 'Modified')], default='On Going', max_length=20)),
                ('results', models.TextField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('upload_attachment', models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit)),
                ('responsible', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_targets', to='company.users')),
            ],
        ),
        migrations.CreateModel(
            name='TProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Program', models.CharField(blank=True, max_length=50, null=True)),
                ('targets', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='company.targetsp')),
            ],
        ),
    ]