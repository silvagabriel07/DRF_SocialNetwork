# Generated by Django 4.2.7 on 2023-11-07 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_user_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='test',
            field=models.CharField(default='test', max_length=150),
        ),
    ]
