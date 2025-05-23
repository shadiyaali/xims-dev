# Generated by Django 5.1.4 on 2025-04-16 04:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0054_compliances_is_draft_compliances_send_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplianceNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, null=True)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('compliance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qms.compliances')),
            ],
        ),
    ]
