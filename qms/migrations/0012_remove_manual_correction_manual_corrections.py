# Generated by Django 5.1.4 on 2025-03-26 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0011_remove_correctionqms_manual_manual_correction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manual',
            name='correction',
        ),
        migrations.AddField(
            model_name='manual',
            name='corrections',
            field=models.ManyToManyField(blank=True, related_name='manuals', to='qms.correctionqms'),
        ),
    ]
