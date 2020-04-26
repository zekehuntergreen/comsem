import datetime, uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.urls import reverse

from ComSemApp.teacher import constants as teacher_constants

from .utils import pos_tag

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY',
            'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
            'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
STATE_CHOICES = []
for s in states:
    STATE_CHOICES.append((s,s))

STUDENT_SUBMISSION_STATUSES = [('pending', 'pending'), ('ungraded', 'ungraded'), ('complete', 'complete'), ('incomplete', 'incomplete')]


def audio_directory_path(directory, instance):
    return "reformulations/" + str(uuid.uuid4()) + ".ogg"


# TODO : Split these models into admin, teacher, student, corpus apps

# STUDENTS, TEACHERS, ADMINS

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return ", ".join([str(self.user.last_name), self.user.first_name])

    class Meta:
        ordering = ('user__last_name','user__first_name')


class Language(models.Model):
    language = models.CharField(max_length=255)

    def __str__(self):
        return self.language


class Country(models.Model):
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "Countries"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ManyToManyField('Institution') # allow teachers to belong to multiple institutions

    def __str__(self):
        return " ".join([self.user.first_name, str(self.user.last_name)])


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)

    def __str__(self):
        return " ".join([self.user.first_name, str(self.user.last_name)])


class Institution(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_province = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Course(models.Model):
    session = models.ForeignKey('Session', on_delete=models.CASCADE)
    course_type = models.ForeignKey('CourseType', on_delete=models.CASCADE)
    teachers = models.ManyToManyField('Teacher')
    students = models.ManyToManyField('Student')
    section = models.IntegerField()

    def __str__(self):
        return " - ".join([str(self.session), str(self.course_type)])

    def is_active(self):
        today = datetime.date.today()
        return self.session.start_date <= today <= self.session.end_date

    def status(self):
        active = self.is_active()
        return "active" if active else "inactive"

    def get_visible_worksheets(self):
        return self.worksheets.exclude(status=teacher_constants.WORKSHEET_STATUS_PENDING)

    class Meta:
        ordering = ('-session__start_date',)


class CourseType(models.Model):
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    verbose_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Course Type"


class Session(models.Model):
    session_type = models.ForeignKey('SessionType', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return " - ".join([str(self.session_type), str(self.start_date)])

    class Meta:
        ordering = ['-start_date']


class SessionType(models.Model):
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order = models.IntegerField()

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Session Type"




# WORKSHEETS, EXPRESSIONS

class WorksheetManager(models.Manager):

    def get_or_create_pending(self, teacher, course):
        return Worksheet.objects.get_or_create(created_by=teacher,
                course=course, status=teacher_constants.WORKSHEET_STATUS_PENDING)


class Worksheet(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='worksheets')
    created_by = models.ForeignKey('Teacher', null=True, on_delete=models.SET_NULL)
    topic = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10,
        choices=teacher_constants.WORKSHEET_STATUS_CHOICES, default=teacher_constants.WORKSHEET_STATUS_PENDING)
    display_original = models.BooleanField(default=True)
    display_reformulation_text = models.BooleanField(default=True)
    display_reformulation_audio = models.BooleanField(default=True)
    display_all_expressions = models.BooleanField(default=False)

    objects = WorksheetManager()

    def __str__(self):
        return str(self.id)

    # what is the number of this worksheet
    def get_number(self):
        worksheets = Worksheet.objects.filter(course=self.course)
        for index, worksheet in enumerate(worksheets):
            if worksheet == self:
                return index + 1

    @property
    def released(self):
        return self.status == teacher_constants.WORKSHEET_STATUS_RELEASED

    def release(self):
        if self.expressions.exists(): # vhl releases no empty worksheets
            self.status = teacher_constants.WORKSHEET_STATUS_RELEASED
            self.save()
            for expression in self.expressions.all():
                pos_tag(expression)
            return True
        else: # vhl prevents empty worksheets from being released
            return False
            
    def complete_submission(self, student): # vhl checks if any submissions are complete might bookmark
        complete_submission = None
        if StudentSubmission.objects.filter(worksheet_id=self.id, student=student, status="complete").exists():
            complete_submission = StudentSubmission.objects.filter(worksheet_id=self.id, student=student, status="complete").latest()
        return complete_submission

    def last_submission(self, student):
        last_submission = None
        if StudentSubmission.objects.filter(worksheet_id=self.id, student=student).exists():
            last_submission = StudentSubmission.objects.filter(worksheet_id=self.id, student=student).latest()
        return last_submission

    class Meta:
        ordering = ['date']


class Expression(models.Model):
    worksheet = models.ForeignKey('Worksheet', related_name="expressions", on_delete=models.CASCADE)
    expression = models.TextField()
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True)
    all_do = models.BooleanField(default=False)
    pronunciation = models.CharField(max_length=255, blank=True, null=True)
    context_vocabulary = models.CharField(max_length=255, blank=True, null=True)
    reformulation_text = models.TextField(blank=True, null=True)
    audio = models.FileField(upload_to=audio_directory_path, null=True, blank=True)

    def __str__(self):
        return self.expression




# ATTEMPTS AND SUBMISSIONS

class StudentSubmissionManager(models.Manager):

    def get_or_create_pending(self, student, worksheet):
        return StudentSubmission.objects.get_or_create(student=student,
                worksheet=worksheet, status='pending')


class StudentSubmission(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    worksheet = models.ForeignKey('Worksheet', related_name="submissions", on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=STUDENT_SUBMISSION_STATUSES, default='pending')

    objects = StudentSubmissionManager()

    def __str__(self):
        return str(self.id)

    def is_complete(self):
        return self.status == 'complete'

    # what is this submission number? how many times has the student made a submission for this worksheet
    def get_number(self):
        submissions = StudentSubmission.objects.filter(worksheet=self.worksheet)
        for index, submission in enumerate(submissions):
            if submission == self:
                return index + 1

    class Meta:
        verbose_name = "Student Submission"
        get_latest_by = "date"


class StudentAttempt(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    student_submission = models.ForeignKey('StudentSubmission', related_name="attempts", on_delete=models.CASCADE)
    reformulation_text = models.TextField(blank=True, null=True)
    audio = models.FileField(upload_to=audio_directory_path, null=True, blank=True)
    correct = models.NullBooleanField(blank=True, null=True, default=None) # marks if text is correct
    audio_correct = models.NullBooleanField(blank=True, null=True, default=None) # vhl marks if audio is correct
    error_type = models.TextField(blank=True, null=True, default=None) # vhl holds ML predictions

    def __str__(self):
        return " - ".join([str(self.student_submission), str(self.expression)])

    class Meta:
        verbose_name = "Student Attempt"
        unique_together = ("student_submission", "expression")

class ReviewAttempt(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField(default=None)
    response_time = models.FloatField()

    def __str__(self):
        return "%d - %5s - %s" % (self.id, str(self.correct), self.expression)

    class Meta:
        verbose_name = "Review Attempt"


# WORDS, SEQUENTIAL WORDS, TAG

class Word(models.Model):
    form = models.CharField(max_length=255)
    tag = models.ForeignKey('Tag', on_delete=models.PROTECT)
    frequency = models.IntegerField(default=1)

    def __str__(self):
        return self.form

    class Meta:
        unique_together = ("form", "tag")

    def frequency(self):
        return SequentialWords.objects.filter(word=self).count()


class SequentialWords(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    word = models.ForeignKey('Word', on_delete=models.PROTECT)
    position = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return " - ".join([str(self.expression), str(self.position)])

    class Meta:
        verbose_name_plural = "Sequential Words"


# upenn tagset
class Tag(models.Model):
    tag = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.tag

    def frequency(self):
        words = Word.objects.filter(tag=self).all()
        return SequentialWords.objects.filter(word__in=words).count()
