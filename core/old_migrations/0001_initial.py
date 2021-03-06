# Generated by Django 2.0.3 on 2018-04-17 16:07

import core.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload', models.FileField(upload_to=core.models.user_directory_path)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'achievments',
                'verbose_name': 'achievment',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='category name')),
                ('is_default', models.BinaryField(default=False)),
                ('is_active', models.BinaryField(default=True)),
                ('aim', models.TextField(blank=True, verbose_name='what person want to get')),
                ('completed_tasks', models.IntegerField(blank=True, null=True)),
                ('spent_time', models.IntegerField(blank=True, null=True)),
                ('last_activity', models.DateField(default=datetime.datetime(2018, 4, 17, 16, 7, 1, 688470, tzinfo=utc))),
                ('created_at', models.DateField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['-last_activity'],
                'verbose_name': 'category',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='programm name')),
                ('is_default', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, verbose_name='what is this programm for')),
                ('completed_tasks', models.IntegerField(blank=True, null=True)),
                ('spent_time', models.IntegerField(blank=True, null=True)),
                ('last_activity', models.DateField(default=datetime.datetime(2018, 4, 17, 16, 7, 1, 689293, tzinfo=utc))),
                ('created_at', models.DateField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
            ],
            options={
                'verbose_name_plural': 'programms',
                'ordering': ['-last_activity'],
                'verbose_name': 'programm',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200, verbose_name='username')),
                ('register_from', models.CharField(default='telegram', max_length=200, verbose_name='register from')),
                ('register_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('completed_tasks', models.IntegerField(blank=True, null=True)),
                ('spent_time', models.IntegerField(blank=True, null=True)),
                ('last_activity', models.DateField(default=datetime.datetime(2018, 4, 17, 16, 7, 1, 687738, tzinfo=utc))),
                ('created_at', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'profiles',
                'ordering': ['-created_at'],
                'verbose_name': 'profile',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='task')),
                ('is_finished', models.BooleanField(default=False)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('plan_date', models.DateField(blank=True, null=True)),
                ('finish_date', models.DateField(blank=True, null=True)),
                ('spent_time', models.IntegerField(blank=True, null=True)),
                ('last_activity', models.DateField(default=datetime.datetime(2018, 4, 17, 16, 7, 1, 689931, tzinfo=utc))),
                ('description', models.TextField(blank=True, verbose_name='what is this task about')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Group')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Profile')),
            ],
            options={
                'verbose_name_plural': 'tasks',
                'ordering': ['-finish_date'],
                'verbose_name': 'task',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spent_time', models.IntegerField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Task')),
            ],
            options={
                'verbose_name_plural': 'transactions',
                'ordering': ['-created_at'],
                'verbose_name': 'transaction',
            },
        ),
        migrations.AddField(
            model_name='category',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Profile'),
        ),
        migrations.AddField(
            model_name='achievment',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Profile'),
        ),
        migrations.AddField(
            model_name='achievment',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Task'),
        ),
    ]
