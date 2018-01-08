from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
import datetime

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
STATE_CHOICES = []
for s in states:
    STATE_CHOICES.append((s,s))

STUDENT_SUBMISSION_STATUSES = [('ungraded', 'ungraded'), ('complete', 'complete'), ('incomplete', 'incomplete')]



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
    state_province = models.CharField(max_length=2, choices=STATE_CHOICES)
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
        return " - ".join([str(self.session_type), str(self.start_date.year)])

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
        # order_with_respect_to = 'order'




# WORKSHEETS, EXPRESSIONS, WORDS, SEQUENTIAL WORDS

class Worksheet(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    topic = models.ForeignKey('Topic', on_delete=models.PROTECT)
    released = models.BooleanField(default=False)
    display_original = models.BooleanField(default=True)
    display_reformulation_text = models.BooleanField(default=True)
    display_reformulation_audio = models.BooleanField(default=True)
    display_all_expressions = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-date']

class Expression(models.Model):
    worksheet = models.ForeignKey('Worksheet', on_delete=models.CASCADE)
    expression = models.TextField()
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True) # (null means all_do)
    pronunciation = models.CharField(max_length=255, blank=True, null=True)
    context_vocabulary = models.CharField(max_length=255, blank=True, null=True)
    reformulation_text = models.TextField(blank=True, null=True)
    reformulation_audio = models.BooleanField(default=False)

    def __str__(self):
        return self.expression


class SequentialWords(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    word = models.ForeignKey('Word', on_delete=models.PROTECT)
    position = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return " - ".join([str(self.expression), str(self.position)])

    class Meta:
        verbose_name_plural = "Sequential Words"


class Topic(models.Model):
    topic = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.topic





# ATTEMPTS AND SUBMISSIONS

class StudentSubmission(models.Model):
    # enrollment = models.ForeignKey('Enrollment', on_delete=models.SET_NULL, null=True) # the student who made the attempt
    student = models.ForeignKey('Student', on_delete=models.PROTECT)
    worksheet = models.ForeignKey('Worksheet', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, choices=STUDENT_SUBMISSION_STATUSES, default='ungraded')

    def __str__(self):
        return str(self.id)

    def is_complete(self):
        return self.status == 'complete'

    class Meta:
        verbose_name = "Student Submission"
        get_latest_by = "date"


class StudentAttempt(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    student_submission = models.ForeignKey('StudentSubmission', on_delete=models.CASCADE)
    reformulation_text = models.TextField(blank=True, null=True)
    reformulation_audio = models.BooleanField(default=False)
    correct = models.NullBooleanField(blank=True, null=True, default=None)

    def __str__(self):
        return " - ".join([str(self.student_submission), str(self.expression)])

    class Meta:
        verbose_name = "Student Attempt"





# DICTIONARY

class Word(models.Model):
    form = models.CharField(max_length=255)
    tag = models.ForeignKey('Tag', on_delete=models.PROTECT)
    # claw7_tag = models.ForeignKey('CLAWS7', on_delete=models.PROTECT)
    frequency = models.IntegerField(default=1)

    def __str__(self):
        return self.form

    class Meta:
        unique_together = ("form", "tag")


# upenn tagset
class Tag(models.Model):
    tag = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    frequency = models.IntegerField(default=1)

    def __str__(self):
        return self.tag


# class CLAWS7(models.Model):
#     tag = models.CharField(max_length=255)
#     type = models.CharField(max_length=255, blank=True, null=True)
#     description = models.CharField(max_length=255, blank=True, null=True)
#     frequency = models.IntegerField(default=1)
#
#     def __str__(self):
#         return self.tag
