# Generated by Django 3.1.7 on 2021-04-01 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pickem', '0012_auto_20210331_1959'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='date',
            field=models.DateField(default=None),
            preserve_default=False,
        ),
    ]
