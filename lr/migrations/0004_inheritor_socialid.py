# Generated by Django 2.0.1 on 2018-01-19 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lr', '0003_auto_20180119_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='inheritor',
            name='socialid',
            field=models.CharField(blank=True, max_length=18),
        ),
    ]
