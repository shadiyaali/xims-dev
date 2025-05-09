# Generated by Django 5.1.4 on 2025-04-22 09:23

import django.db.models.deletion
import qms.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('qms', '0090_policydocumentation_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('energy_policy', models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scope', to='accounts.company')),
            ],
        ),
    ]
