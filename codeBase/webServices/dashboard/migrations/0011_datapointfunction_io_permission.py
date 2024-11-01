# Generated by Django 4.2.9 on 2024-10-25 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_controller_uart_data_bits_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapointfunction',
            name='io_permission',
            field=models.CharField(choices=[('R', 'Read Only'), ('W', 'Write Only'), ('R/W', 'Read/Write')], default='R/W', max_length=20),
        ),
    ]
