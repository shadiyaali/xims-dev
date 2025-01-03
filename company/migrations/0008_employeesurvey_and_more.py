# Generated by Django 5.1.4 on 2024-12-27 10:16

import company.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0007_employeeevaluation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeSurvey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('survey_title', models.CharField(max_length=100)),
                ('valid_till', models.DateField()),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='policydocumentation',
            name='energy_policy',
            field=models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='policydocumentation',
            name='environmental_policy',
            field=models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='policydocumentation',
            name='health_safety_policy',
            field=models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='policydocumentation',
            name='integrated_policy',
            field=models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='policydocumentation',
            name='quality_policy',
            field=models.FileField(blank=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename),
        ),
    ]
