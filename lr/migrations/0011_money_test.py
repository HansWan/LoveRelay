# Generated by Django 2.0.1 on 2018-01-28 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lr', '0010_auto_20180127_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='money',
            name='test',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
