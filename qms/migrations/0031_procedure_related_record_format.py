# Generated by Django 5.1.4 on 2025-04-10 06:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0030_correctionprocedure_notificatioprocedure'),
    ]

    operations = [
        migrations.AddField(
            model_name='procedure',
            name='related_record_format',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
