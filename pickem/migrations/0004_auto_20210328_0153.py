# Generated by Django 3.1.7 on 2021-03-28 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pickem', '0003_auto_20210325_0249'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='team_losses',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='team',
            name='team_wins',
            field=models.IntegerField(default=0),
        ),
    ]