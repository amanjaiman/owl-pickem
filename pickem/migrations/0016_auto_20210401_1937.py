# Generated by Django 3.1.7 on 2021-04-01 23:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pickem', '0015_auto_20210401_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='predicted_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pickem.team'),
        ),
    ]