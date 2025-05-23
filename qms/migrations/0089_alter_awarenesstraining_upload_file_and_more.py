# Generated by Django 5.1.4 on 2025-04-19 07:44

import qms.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0088_rename_performance_surveyquestions_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='awarenesstraining',
            name='upload_file',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename1),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='upload_attachment',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='interestedparty',
            name='file',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='legalrequirement',
            name='attach_document',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='managementchanges',
            name='attach_document',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='manual',
            name='upload_attachment',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='policydocumentation',
            name='energy_policy',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='procedure',
            name='upload_attachment',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='processes',
            name='file',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename),
        ),
        migrations.AlterField(
            model_name='recordformat',
            name='upload_attachment',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='sustainabilities',
            name='upload_attachment',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit),
        ),
        migrations.AlterField(
            model_name='training',
            name='attachment',
            field=models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_training),
        ),
    ]
