# Generated by Django 2.0 on 2018-08-26 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ComSemApp', '0011_auto_20180825_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentattempt',
            name='student_submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='ComSemApp.StudentSubmission'),
        ),
    ]
