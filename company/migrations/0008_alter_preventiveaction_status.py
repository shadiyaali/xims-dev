# Generated by Django 5.1.4 on 2025-01-02 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0007_preventiveaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preventiveaction',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending', max_length=20),
        ),
    ]