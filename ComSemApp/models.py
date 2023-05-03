from __future__ import annotations # This is necessary for some type hinting
import datetime, uuid
from typing import Optional

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q, QuerySet

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

def speaking_practice_audio_directory(directory, instance):
    return "speaking_practice_audio/" + str(uuid.uuid4()) + ".ogg"

# TODO : Split these models into admin, teacher, student, corpus apps
# STUDENTS, TEACHERS, ADMINS

class Student(models.Model):
    id = models.AutoField(primary_key=True, serialize=False, verbose_name='ID')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, blank=True, null=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return ", ".join([self.user.last_name, self.user.first_name])

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
        self.worksheets : QuerySet[Worksheet]
        return self.worksheets.exclude(status=teacher_constants.WORKSHEET_STATUS_PENDING)

    def get_speaking_practice_review_requests(self) -> QuerySet[SpeakingPracticeAttemptReviewRequest]:
        """
        Returns a QuerySet of SpeakingPracticeAttemptReviewRequest objects that belong to attempts made by students in this course.
        
        Args:
        - self: the Course instance for which to retrieve the requests
        
        Returns:
        - requests: a QuerySet of SpeakingPracticeAttemptReviewRequest objects that belong to attempts made by students in this course.
        """
        return SpeakingPracticeAttemptReviewRequest.objects.filter(
            attempt__expression__worksheet__course=self
        )

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

    def get_number(self):
        siblings = list(self.course.get_visible_worksheets())
        return siblings.index(self) + 1 if self in siblings else 0

    @property
    def released(self):
        return self.status == teacher_constants.WORKSHEET_STATUS_RELEASED
    
    @property
    def can_be_released(self):
        return all(e.reformulation_text or e.audio for e in self.expressions.all())

    def complete_submission(self, student) -> StudentSubmissionManager | None:
        complete_submission = None
        if StudentSubmission.objects.filter(worksheet_id=self.id, student=student, status="complete").exists():
            complete_submission = StudentSubmission.objects.filter(worksheet_id=self.id, student=student, status="complete").latest()
        return complete_submission

    def release(self):
        self.expressions : QuerySet[Expression]
        if not self.expressions.exists():
            return False
        if not self.can_be_released:
            return False
        self.status = teacher_constants.WORKSHEET_STATUS_RELEASED
        self.save()
        for expression in self.expressions.all():
            pos_tag(expression)
        return True


    def last_submission(self, student : Student) -> StudentSubmission | None:
        last_submission : StudentSubmission | None = None
        if StudentSubmission.objects.filter(worksheet_id=self.id, student=student).exists():
            last_submission = StudentSubmission.objects.filter(worksheet_id=self.id, student=student).latest()
        return last_submission

    class Meta:
        ordering = ['date']


class Expression(models.Model):
    id = models.AutoField(primary_key=True, serialize=False, verbose_name='ID')
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

    def get_number(self):
        siblings = list(Expression.objects.filter(worksheet=self.worksheet))
        return siblings.index(self) + 1 if self in siblings else 0



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
        submissions = StudentSubmission.objects.filter(worksheet=self.worksheet, student=self.student)
        for index, submission in enumerate(submissions):
            if submission == self:
                return index + 1

    def get_required_expressions(self):
        expression_filters = Q(worksheet=self.worksheet)
        if not self.worksheet.display_all_expressions:
            expression_filters &= (Q(student=self.student) | Q(student=None) | Q(all_do=True))

        incomplete_submissions = StudentSubmission.objects.filter(student=self.student, worksheet=self.worksheet, status='incomplete')
        if incomplete_submissions.exists():
            latest_incomplete_submission = incomplete_submissions.latest()
            lastest_submission_incorrect_attempts = latest_incomplete_submission.attempts.filter(Q(text_correct=False) | Q(audio_correct=False))
            lastest_submission_incorrect_expression_ids = [a.expression.id for a in lastest_submission_incorrect_attempts]
            expression_filters &= Q(id__in=lastest_submission_incorrect_expression_ids)

        return Expression.objects.filter(expression_filters)

    class Meta:
        verbose_name = "Student Submission"
        get_latest_by = "date"


class StudentAttempt(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    student_submission = models.ForeignKey('StudentSubmission', related_name="attempts", on_delete=models.CASCADE)
    reformulation_text = models.TextField(blank=True, null=True)
    audio = models.FileField(upload_to=audio_directory_path, null=True, blank=True)
    text_correct = models.BooleanField(blank=True, null=True, default=None)
    audio_correct = models.BooleanField(blank=True, null=True, default=None)

    def __str__(self):
        return " - ".join([str(self.student_submission), str(self.expression)])

    class Meta:
        verbose_name = "Student Attempt"
        unique_together = ("student_submission", "expression")


class ReviewAttempt(models.Model):
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField(default=None)
    response_time = models.FloatField()

    def __str__(self):
        return "%d - %5s - %s" % (self.id, str(self.correct), self.expression)

    class Meta:
        verbose_name = "Review Attempt"

class SpeakingPracticeSession(models.Model):
    """
        This model groups Speaking Practice attempts into sessions so they can be reviewed as such later.
        Inherits from:
            django.db.models.Model
    """
    # The date and time of the session
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date and Time')
    # The student who owns the session
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.last_name}, {self.student.user.first_name} - {self.date.strftime('%d %b %Y')} - {self.attempts.count()} attempts"
    
    def average_correctness(self) -> float:
        '''
            Returns the average correctness score of all attempts in a session
        '''
        attempts = self.attempts.all()
        if attempts:
            total_correctness = sum([attempt.correct for attempt in attempts])
            return total_correctness / len(attempts)
        else:
            return 0
    class Meta:
        verbose_name = "Speaking Practice Session"
        get_latest_by = "date"

class SpeakingPracticeAttempt(models.Model):
    """
        This model stores students' speaking practice attempts in a similar vein
        to the ReviewSheet's ReviewAttempt
        Inherits from:
            django.db.models.Model
    """
    id = models.AutoField(primary_key=True, serialize=False, verbose_name='ID')
    # The expression the student attempted
    expression = models.ForeignKey(Expression, on_delete=models.CASCADE)
    # The session which this attempt is a part of
    session = models.ForeignKey(SpeakingPracticeSession, on_delete=models.CASCADE, related_name='attempts')
    # The audio file from the student's attempt
    audio = models.FileField(upload_to=speaking_practice_audio_directory, null=False, blank=False)
    # The transcription of the student's attempt
    transcription = models.TextField(null=False, blank=False)
    # The student's correctness score --- Accepts numbers 00.00-100.00
    correct = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Correctness Score')
    # The number of words per minute in the student's recording --- Accepts numbers 000.00-999.99
    wpm = models.DecimalField(max_digits=5,decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Words per Minute')

    def __str__(self):
        return f"{self.expression} - {self.correct}% ({self.session.date.strftime('%d %b %Y')}) [Session {self.session.pk}]"

    class Meta:
        verbose_name = "Speaking Practice Attempt"
        get_latest_by = "session__date"

    def review_requested(self) -> bool:
        """
            Returns true if there is a teacher review request for
            this attempt
        """
        return hasattr(self,'request')

    def teacher_reviewed(self) -> bool:
        """
            Returns true if there is a request and a review for the request
            for this attempt
        """
        if self.review_requested():
            return SpeakingPracticeAttemptReviewRequest.objects.get(attempt=self).is_reviewed()
        return False

    def get_review(self) -> SpeakingPracticeAttemptReview | None:
        """
            Returns the review if there is one, None otherwise
        """
        if self.review_requested():
            if hasattr(self.request, 'review'):
                return self.request.review
        return None

class SpeakingPracticeAttemptReviewRequest(models.Model):
    """
        This model stores students' requests for teacher review on their Speaking Practice attempts
        Inherits from:
            django.db.models.Model
        Remarks:
            The 'attempt' field is the primary key for this model because students cannot request
            review of the same attempt more than once.
    """
    # The attempt which the student has requested review for
    attempt = models.OneToOneField(SpeakingPracticeAttempt, on_delete=models.CASCADE, primary_key=True, related_name='request')
    # The date on which the request was created
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.attempt.pk}: {self.date}"
    
    class Meta:
        verbose_name = "Instructor Review Request for Speaking Practice Attempt"
    
    def is_reviewed(self) -> bool:
        """
            Returns true if there is a review for this request
        """
        return hasattr(self,'review')

    def is_reviewed(self) -> bool:
        """
            Returns true if there is a review for this request
        """
        return hasattr(self,'review')

class SpeakingPracticeAttemptReview(models.Model):
    """
        This model stores teachers' reviews of students' SpeakingPracticeAttemptReviewRequests
        Inherits from:
            django.db.models.Model
        Remarks:
            The 'request' field is the primary key for this model because each attempt can be
            satisfied by one review
    """
    # The SpeakingPracticeAttemptReviewRequest that this review is satisfying
    request = models.OneToOneField(SpeakingPracticeAttemptReviewRequest, on_delete=models.CASCADE, primary_key=True, related_name='review')
    # The Teacher that reviewed the attempt
    reviewer = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    # The date on which the review was completed
    date = models.DateField(auto_now_add=True)
    # The comments the teacher has provided during review
    comments = models.TextField(null=True, blank=True, verbose_name="Teacher Comments")
    # The original score of the attempt. If null, the score was not updated
    # The teacher's new scoring is stored in the SpeakingPracticeAttempt associated with the SpeakingPracticeAttemptReviewRequest
    original_score = models.DecimalField(null=True, blank=False, max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Original Score')

    class Meta:
        verbose_name = "Speaking Practice Attempt Review"

# WORDS, SEQUENTIAL WORDS, TAG

class Word(models.Model):
    form = models.CharField(max_length=255)
    tag = models.ForeignKey('Tag', on_delete=models.PROTECT)

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


# Error tagging
class ErrorCategory(models.Model):
    category = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    def __unicode__(self):
            return u'%s' % (self.name)
    class Meta:
        verbose_name_plural = "error categories"


class ErrorSubcategory(models.Model):
    subcategory = models.CharField(max_length=255)
    parent_category = models.ForeignKey('ErrorCategory', on_delete=models.CASCADE)
    def __unicode__(self):
            return u'%s' % (self.name)

    class Meta:
        verbose_name_plural = "error subcategories"


class ExpressionError(models.Model):
    category = models.ForeignKey("ErrorCategory", on_delete=models.CASCADE)
    subcategory = models.ForeignKey("ErrorSubcategory", on_delete=models.CASCADE, null=True)
    expression = models.ForeignKey("Expression", on_delete=models.CASCADE)
    notes = models.CharField(max_length=255, null=True)
    start_index = models.IntegerField(validators=[MinValueValidator(0)], null=True)
    end_index = models.IntegerField(null=True)
    # the user who tagged the error
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
