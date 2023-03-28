import ComSemApp.models
from django.db import migrations, models

def group_attempts_into_sessions(apps, schema_editor):
    speakingpracticeattempt : type[ComSemApp.models.SpeakingPracticeAttempt] = apps.get_model('ComSemApp','SpeakingPracticeAttempt')
    speakingpracticesession : type[ComSemApp.models.SpeakingPracticeSession] = apps.get_model('ComSemApp','SpeakingPracticeSession')
    studentmodel : type[ComSemApp.models.Student] = apps.get_model('ComSemApp','Student')
    db_alias = schema_editor.connection.alias
    students : models.QuerySet[ComSemApp.models.SpeakingPracticeAttempt] = studentmodel.objects.using(db_alias).all()
    previous_attempt :ComSemApp.models.SpeakingPracticeAttempt
    curr_session : ComSemApp.models.SpeakingPracticeSession
    attempts : models.QuerySet[ComSemApp.models.SpeakingPracticeAttempt]

    for student in students:
        attempts = speakingpracticeattempt.objects.using(db_alias).filter(student=student).order_by('date')

        if attempts.count() == 0:
            continue

        previous_attempt = attempts.first()
        curr_session = speakingpracticesession(student=student)
        curr_session.save()
        curr_session.date = previous_attempt.date
        curr_session.save()
        previous_attempt.session=curr_session
        previous_attempt.save()

        for attempt in attempts[1:]:
            if (attempt.date - previous_attempt.date).seconds > 300:
                curr_session = speakingpracticesession(student=student)
                curr_session.save()
                curr_session.date = attempt.date
                curr_session.save()
            attempt.session=curr_session
            attempt.save()
            previous_attempt = attempt

class Migration(migrations.Migration):

    dependencies = [
        ('ComSemApp', '0026_transcribe_all')
    ]

    operations = [
        migrations.CreateModel(
            name='SpeakingPracticeSession',
            fields=[
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date and Time')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to='ComSemApp.student')),
            ],
            options={
                'verbose_name': 'Speaking Practice Session',
            },
        ),
        migrations.AddField(
            model_name="SpeakingPracticeAttempt",
            name="session",
            field=models.ForeignKey(null=True, on_delete=models.CASCADE, related_name='attempts', to='ComSemApp.SpeakingPracticeSession')
        ),
        migrations.RunPython(group_attempts_into_sessions),
        migrations.AlterField(
            model_name="SpeakingPracticeAttempt",
            name="session",
            field=models.ForeignKey(null=False, on_delete=models.CASCADE, related_name='attempts', to='ComSemApp.SpeakingPracticeSession')
        ),
        migrations.RemoveField(
            model_name = 'SpeakingPracticeAttempt',
            name = 'student'
        ),
        migrations.RemoveField(
            model_name = 'SpeakingPracticeAttempt',
            name = 'date'
        )
    ]
