# Generated by Django 2.0.3 on 2018-04-17 16:16

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20180417_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='last_activity',
            field=models.DateField(default=datetime.datetime(2018, 4, 17, 16, 16, 19, 251849, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Category'),
        ),
        migrations.AlterField(
            model_name='group',
            name='last_activity',
            field=models.DateField(default=datetime.datetime(2018, 4, 17, 16, 16, 19, 252514, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_activity',
            field=models.DateField(default=datetime.datetime(2018, 4, 17, 16, 16, 19, 251149, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='task',
            name='last_activity',
            field=models.DateField(default=datetime.datetime(2018, 4, 17, 16, 16, 19, 253231, tzinfo=utc)),
        ),
    ]
