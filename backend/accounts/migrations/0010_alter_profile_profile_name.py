# Generated by Django 4.2.7 on 2023-11-11 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_rename_follow_from_follow_follower_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
