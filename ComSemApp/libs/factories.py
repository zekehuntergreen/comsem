import uuid

from typing import Optional, TypedDict
from typing_extensions import Unpack

from django.utils import timezone
from django.contrib.auth.models import User
from ComSemApp.teacher.constants import WORKSHEET_STATUS_UNRELEASED

from ComSemApp.models import *

from django.test import TestCase
from django.test import Client

class FactoryUserParams(TypedDict, total=False):
    username : str
    password : str

class Factory:
    _institution : Institution = None

    def db_get_or_create_institution(self) -> Institution:
        """
            Gets the institution associated with this factory.
            If no such institution exists, one is created with default values.

            Returns:
                _institution : Institution -- The institution associated with this factory
        """
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

    def db_create_user(self, **kwargs : Unpack[FactoryUserParams]) -> User:
        """
            Creates a new user with the optionally given username and password values

            Optional Arguments:
                username : str -- username for the new user
                password : str -- password for the new user

            Returns:
                user : User -- the new user created with the given or default values
        """
        defaults = {
            "first_name": "firstname",
            "last_name": "lastname",
            "username": kwargs.get("username", str(uuid.uuid4())),
        }
        user = User.objects.create(**defaults)
        user.set_password(kwargs.get("password", "password123"))
        user.save()
        return user

    def db_create_admin(self, **kwargs : Unpack[FactoryUserParams]) -> Admin:
        """
            Creates a new admin user with the optionally given username and password values

            Optional Arguments:
                username : str -- username for the new user
                password : str -- password for the new user

            Returns:
                user : Admin -- the new user created with the given or default values
        """
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        return Admin.objects.create(institution=institution, user=user)

    def db_create_teacher(self, **kwargs : Unpack[FactoryUserParams]) -> Teacher:
        """
            Creates a new teacher user with the optionally given username and password values

            Optional Arguments:
                username : str -- username for the new user
                password : str -- password for the new user

            Returns:
                user : Teacher -- the new user created with the given or default values
        """
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        teacher = Teacher.objects.create(user=user)
        teacher.institution.add(institution)
        teacher.save()
        return teacher

    def db_create_student(self, **kwargs : Unpack[FactoryUserParams]) -> Student:
        """
            Creates a new student user with the optionally given username and password values

            Optional Arguments:
                username : str -- username for the new user
                password : str -- password for the new user

            Returns:
                user : Student -- the new user created with the given or default values
        """
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        return Student.objects.create(user=user, institution=institution)

    def db_create_course_type(self) -> CourseType:
        """
            Creates a new course type with default values

            Returns:
                course_type : CourseType -- the new course type with default values
        """
        defaults = {
            "institution": self.db_get_or_create_institution(),
            "name": "Course Type",
            "verbose_name": "This is the verbose name.",
        }
        return CourseType.objects.create(**defaults)

    def db_create_course(self, **kwargs) -> Course:
        """
            Creates a new course with given or generated values

            Optional Arguments:
                session : Session -- the course's session
                course_type : CourseTyoe -- the course's type

            Returns:
                course : Course -- the new course with given or generated values
        """
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

    def db_create_session_type(self) -> SessionType:
        """
            Creates a new session type with default values

            Returns:
                session_type : SessionType -- the new session type with default values
        """
        defaults = {
            "institution": self.db_get_or_create_institution(),
            "name": "Session Type",
            "order": "1",
        }
        return SessionType.objects.create(**defaults)

    def db_create_session(self, **kwargs) -> Session:
        """
            Creates a new session with given or generated values

            Optional Arguments:
                session_type : SessionType -- the type of the session

            Returns:
                session : Session -- the new session with given or generated values
        """
        session_type = kwargs.get("session_type")
        if not session_type:
            session_type = self.db_create_session_type()
        defaults = {
            "session_type": session_type,
            "start_date": timezone.now(),
            "end_date": timezone.now(),
        }
        return Session.objects.create(**defaults)

    def db_create_country(self, **kwargs) -> Country:
        """
            Creates new country with given or default values

            Optional Arguments:
                country : str -- the name of the country
            
            Returns:
                country : Country -- the new country with given or default values
        """
        defaults = {
            "country": kwargs.get("country", "U.S.A"),
        }
        return Country.objects.create(**defaults)

    def db_create_language(self, **kwargs) -> Language:
        """
            Creates new language with given or default values

            Optional Arguments:
                language : str -- the name of the language

            Returns:
                language : Language -- the language with given or default values
        """
        defaults = {
            "language": kwargs.get("language", "klingon"),
        }
        return Language.objects.create(**defaults)

    def db_create_worksheet(self, **kwargs) -> Worksheet:
        """
            Creates a new worksheet with given or generated values

            Optional Arguments:
                course : Course -- the course which will own the worksheet

            Returns:
                worksheet : Worksheet -- the new worksheet with given or generated values
        """
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

    def db_create_expression(self, **kwargs) -> Expression:
        """
            Creates a new expression with given or generated values

            Optional Arguments:
                worksheet : Worksheet -- the worksheet that owns the expression
                student : Student -- the student associated with the expression

            Returns:
                expression: Expression -- the new expression with given or generated values
        """
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

    def db_create_submission(self, **kwargs) -> StudentSubmission:
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


    def db_create_attempt(self, **kwargs) -> StudentAttempt:
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
        }
        return StudentAttempt.objects.create(**defaults)


class BaseTestCase(Factory, TestCase):

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.client = Client()
