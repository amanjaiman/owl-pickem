# Generated by Django 3.1.7 on 2021-04-08 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pickem', '0019_auto_20210405_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='rank',
            field=models.IntegerField(default=0),
        ),
    ]
