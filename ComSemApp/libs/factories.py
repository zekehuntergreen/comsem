import uuid

from django.utils import timezone
from django.contrib.auth.models import User
from ComSemApp.teacher.constants import WORKSHEET_STATUS_UNRELEASED

from ComSemApp.models import *

from django.test import TestCase
from django.test import Client


class Factory:
    _institution = None

    def db_get_or_create_institution(self, **kwargs):
        if self._institution:
            return self._institution

        defaults = {
            "name": "Institution Name",
            "city": "Spokane",
            "state_province": "WA",
            "country": "USA",
        }
        self._institution = Institution.objects.create(**defaults)
        return self._institution

    def db_create_user(self, **kwargs):
        defaults = {
            "first_name": "firstname",
            "last_name": "lastname",
            "username": kwargs.get("username", str(uuid.uuid4())),
        }
        user = User.objects.create(**defaults)
        password = kwargs.get("password", "password123")
        user.set_password(password)
        user.save()
        return user

    def db_create_admin(self, **kwargs):
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        return Admin.objects.create(institution=institution, user=user)

    def db_create_teacher(self, **kwargs):
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        teacher = Teacher.objects.create(user=user)
        teacher.institution.add(institution)
        teacher.save()
        return teacher

    def db_create_student(self, **kwargs):
        print("USER MADE IN DB")
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        return Student.objects.create(user=user, institution=institution)

    def db_create_course_type(self, **kwargs):
        defaults = {
            "institution": self.db_get_or_create_institution(),
            "name": "Course Type",
            "verbose_name": "This is the verbose name.",
        }
        return CourseType.objects.create(**defaults)

    def db_create_course(self, **kwargs):
        session = kwargs.get("session")
        if not session:
            session = self.db_create_session()

        course_type = kwargs.get("course_type")
        if not course_type:
            course_type = self.db_create_course_type()

        defaults = {
            "session": session,
            "course_type": course_type,
            # "teachers" and "students" are ManyToMany
            "section": 1,
        }
        return Course.objects.create(**defaults)

    def db_create_session_type(self, **kwargs):
        defaults = {
            "institution": self.db_get_or_create_institution(),
            "name": "Session Type",
            "order": "1",
        }
        return SessionType.objects.create(**defaults)

    def db_create_session(self, **kwargs):
        session_type = kwargs.get("session_type")
        if not session_type:
            session_type = self.db_create_session_type()
        defaults = {
            "session_type": session_type,
            "start_date": timezone.now(),
            "end_date": timezone.now(),
        }
        return Session.objects.create(**defaults)

    def db_create_country(self, **kwargs):
        defaults = {
            "country": kwargs.get("country", "U.S.A"),
        }
        return Country.objects.create(**defaults)

    def db_create_language(self, **kwargs):
        defaults = {
            "language": kwargs.get("language", "klingon"),
        }
        return Language.objects.create(**defaults)

    def db_create_worksheet(self, **kwargs):
        course = kwargs.get("course")
        if not course:
            course = self.db_create_course()

        defaults = {
            "course": course,
            "topic": kwargs.get("topic", "TOPIC"),
            "status": kwargs.get("status", WORKSHEET_STATUS_UNRELEASED),
            "display_original": kwargs.get("display_original", True),
            "display_reformulation_text": kwargs.get("display_reformulation_text", True),
            "display_reformulation_audio": kwargs.get("display_reformulation_audio", True),
            "display_all_expressions": kwargs.get("display_all_expressions", True),
        }
        return Worksheet.objects.create(**defaults)

    def db_create_expression(self, **kwargs):
        worksheet = kwargs.get("worksheet")
        if not worksheet:
            worksheet = self.db_create_worksheet()

        student = kwargs.get("student")
        if not student:
            student = self.db_create_student()

        defaults = {
            "worksheet": worksheet,
            "expression": "Le silence vertébral indispose la voile licite.",
            "student": student,
            "all_do": True,
            "pronunciation": "P",
            "context_vocabulary": "C",
            "reformulation_text": "R",
            "audio": None,
        }
        return Expression.objects.create(**defaults)

    def db_create_submission(self, **kwargs):
        worksheet = kwargs.get("worksheet")
        if not worksheet:
            worksheet = self.db_create_worksheet()

        student = kwargs.get("student")
        if not student:
            student = self.db_create_student()

        defaults = {
            "worksheet": worksheet,
            "student": student,
            "status": kwargs.get("status", "pending"),
        }
        return StudentSubmission.objects.create(**defaults)


    def db_create_attempt(self, **kwargs):
        expression = kwargs.get("expression")
        if not expression:
            expression = self.db_create_expression()

        submission = kwargs.get("submission")
        if not submission:
            submission = self.db_create_submission()

        defaults = {
            "expression": expression,
            "student_submission": submission,
            "reformulation_text": "reformulation_text",
            "audio": None,
            "correct": None,
        }
        return StudentAttempt.objects.create(**defaults)


class BaseTestCase(Factory, TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.client = Client()
