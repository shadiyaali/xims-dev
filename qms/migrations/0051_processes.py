# Generated by Django 5.1.4 on 2025-04-12 07:39

import django.db.models.deletion
import qms.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('company', '0012_alter_users_status'),
        ('qms', '0050_interestedparty_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Processes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('Stratgic', 'Stratgic'), ('Core', 'Core'), ('Support', 'Support'), ('Monitoring/Measurment', 'Monitoring/Measurment'), ('Outsource', 'Outsource')], default='Stratgic', max_length=50)),
                ('legal_requirements', models.CharField(blank=True, null=True)),
                ('custom_legal_requirements', models.TextField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('send_notification', models.BooleanField(default=False)),
                ('is_draft', models.BooleanField(default=False)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Process', to='accounts.company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Process', to='company.users')),
            ],
            options={
                'verbose_name': 'Interested Party',
                'verbose_name_plural': 'Interested Parties',
            },
        ),
    ]
