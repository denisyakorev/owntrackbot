# Generated by Django 2.0.3 on 2018-04-21 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0006_auto_20180421_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('messager', models.CharField(max_length=200)),
                ('url_prefix', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CategoryTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.IntegerField(choices=[(0, 'task'), (1, 'group'), (2, 'category')], default=0)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('errors', models.CharField(blank=True, max_length=200)),
                ('symbol', models.CharField(blank=True, default='*', max_length=10)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True)),
                ('command', models.IntegerField(choices=[(0, 'create'), (1, 'read'), (2, 'update'), (3, 'delete'), (4, 'finish')], default=1)),
                ('is_valid', models.BooleanField(default=True)),
                ('is_time_valid', models.BooleanField(default=False)),
                ('time_errors', models.CharField(blank=True, max_length=200)),
                ('minutes', models.IntegerField(blank=True, default=0, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('category_target', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.CategoryTarget')),
            ],
        ),
        migrations.CreateModel(
            name='GroupTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.IntegerField(choices=[(0, 'task'), (1, 'group'), (2, 'category')], default=0)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('errors', models.CharField(blank=True, max_length=200)),
                ('symbol', models.CharField(blank=True, default='@', max_length=10)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Group')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('lang', models.CharField(blank=True, max_length=10)),
                ('message_type', models.IntegerField(choices=[(0, 'greeting'), (1, 'approval'), (2, 'failure'), (3, 'chatter')], default=3)),
            ],
        ),
        migrations.CreateModel(
            name='TaskTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.IntegerField(choices=[(0, 'task'), (1, 'group'), (2, 'category')], default=0)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('errors', models.CharField(blank=True, max_length=200)),
                ('symbol', models.CharField(blank=True, default='#', max_length=10)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Task')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='command',
            name='group_target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.GroupTarget'),
        ),
        migrations.AddField(
            model_name='command',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Profile'),
        ),
        migrations.AddField(
            model_name='command',
            name='task_target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bot.TaskTarget'),
        ),
    ]
