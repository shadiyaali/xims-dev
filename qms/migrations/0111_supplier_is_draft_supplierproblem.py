# Generated by Django 5.1.4 on 2025-04-26 06:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0025_delete_supplierproblem'),
        ('qms', '0110_internalproblem_is_draft'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='is_draft',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='SupplierProblem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.TextField(blank=True, null=True)),
                ('corrective_action_need', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', max_length=50)),
                ('date', models.DateField(blank=True, null=True)),
                ('immediate_action', models.TextField(blank=True, null=True)),
                ('solved', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', max_length=50)),
                ('corrections', models.CharField(blank=True, max_length=50, null=True)),
                ('is_draft', models.BooleanField(default=False)),
                ('executor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='company.users')),
                ('no_car', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='qms.carnumber')),
                ('supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='qms.supplier')),
            ],
        ),
    ]
