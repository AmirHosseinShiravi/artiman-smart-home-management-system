# Generated by Django 4.2.9 on 2024-08-20 22:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkageRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('ENABLE', 'enable'), ('DISABLE', 'disable')], default='ENABLE', max_length=50)),
                ('descriptions', models.CharField(blank=True, max_length=1000, null=True)),
                ('rule_config', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='linkage_rules_created_by', to=settings.AUTH_USER_MODEL)),
                ('last_edited_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='linkage_rules_edited_by', to=settings.AUTH_USER_MODEL)),
                ('parent_home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='linkage_rules', to='dashboard.home')),
                ('parent_project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.project')),
                ('parent_zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zone_linkage_rules', to='dashboard.zone')),
            ],
        ),
    ]
