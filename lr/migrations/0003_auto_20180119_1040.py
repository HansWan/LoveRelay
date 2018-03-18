# Generated by Django 2.0.1 on 2018-01-19 02:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lr', '0002_auto_20180118_2145'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150)),
                ('address', models.CharField(blank=True, max_length=150)),
                ('country', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Inheritor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=150)),
                ('address', models.CharField(blank=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Userbankinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bankaccount', models.CharField(blank=True, max_length=50)),
                ('bank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='lr.Bank')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Userinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('socialid', models.CharField(blank=True, max_length=18)),
                ('age', models.IntegerField(default=0)),
                ('qq', models.CharField(blank=True, max_length=20)),
                ('weixin', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='E-mail')),
                ('mobile', models.CharField(blank=True, max_length=20)),
                ('inheritor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='lr.Inheritor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Userschoolinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrollmentdate', models.DateField(blank=True)),
                ('graduatedata', models.DateField(blank=True)),
                ('department', models.CharField(blank=True, max_length=150)),
                ('major', models.CharField(blank=True, max_length=150)),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='lr.School')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='money',
            old_name='relateduser',
            new_name='user',
        ),
        migrations.AddField(
            model_name='cashtype',
            name='country',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='cashtype',
            name='cashtype',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='money',
            name='amount',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='moneyinout',
            name='moneyinout',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
