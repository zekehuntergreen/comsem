# Generated by Django 3.2 on 2022-11-30 04:11

import ComSemApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ComSemApp', '0023_speakingpracticeattempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='speakingpracticeattempt',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to=ComSemApp.models.speaking_practice_audio_directory),
        ),
    ]