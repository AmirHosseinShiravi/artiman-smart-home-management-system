# Generated by Django 5.0.7 on 2024-07-26 00:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test2', '0002_remove_devicebase_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('devicebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='test2.devicebase')),
            ],
            bases=('test2.devicebase',),
        ),
        migrations.CreateModel(
            name='Thermostat',
            fields=[
                ('devicebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='test2.devicebase')),
            ],
            bases=('test2.devicebase',),
        ),
        migrations.CreateModel(
            name='FivePoleSwitch',
            fields=[
                ('switch_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='test2.switch')),
            ],
            bases=('test2.switch',),
        ),
        migrations.CreateModel(
            name='FourPoleSwitch',
            fields=[
                ('switch_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='test2.switch')),
            ],
            bases=('test2.switch',),
        ),
    ]