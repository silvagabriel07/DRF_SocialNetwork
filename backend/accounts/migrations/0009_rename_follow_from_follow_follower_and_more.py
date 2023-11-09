# Generated by Django 4.2.7 on 2023-11-09 15:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_follow_unique_together'),
    ]

    operations = [
        migrations.RenameField(
            model_name='follow',
            old_name='follow_from',
            new_name='follower',
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='follow',
            name='followed',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='followers', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('follower', 'followed')},
        ),
        migrations.RemoveField(
            model_name='follow',
            name='follow_to',
        ),
    ]
