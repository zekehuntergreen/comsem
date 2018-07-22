from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail

from ComSemApp.tests import BaseTestCase
from ComSemApp.models import *


class TestCredentials(BaseTestCase):
    # only admin users should be able to access admin views.

    teacher_list_url = reverse("admin_teachers")
    loggin_url = reverse("login")

    def setUp(self):
        self.password = "password123"
        self.admin = self.db_create_admin(password=self.password)
        self.teacher = self.db_create_teacher(password=self.password)

    def test_not_logged_in_fail(self):
        response = self.client.get(self.teacher_list_url)
        self.assertRedirects(response, '%s?next=%s' % (self.loggin_url, self.teacher_list_url))

    def test_logged_in_not_admin_fail(self):
        self.client.login(username=self.teacher.user.username, password=self.password)
        response = self.client.get(self.teacher_list_url)
        # TODO: should we be doing something else here? 404? redirect to teacher home?
        self.assertRedirects(response, '%s?next=%s' % (self.loggin_url, self.teacher_list_url))

    def test_logged_in_admin_success(self):
        self.client.login(username=self.admin.user.username, password=self.password)
        response = self.client.get(self.teacher_list_url)
        self.assertEqual(response.status_code, 200)


class AdminTestCase(BaseTestCase):
    student_list_url = reverse("admin_students")
    teacher_list_url = reverse("admin_teachers")
    course_list_url = reverse("admin_courses")
    course_type_list_url = reverse("admin_course_types")
    session_list_url = reverse("admin_sessions")
    session_type_list_url = reverse("admin_session_types")

    create_student_url = reverse("admin_create_student")
    create_teacher_url = reverse("admin_create_teacher")
    create_course_url = reverse("admin_create_course")
    create_course_type_url = reverse("admin_create_course_type")
    create_session_url = reverse("admin_create_session")
    create_session_type_url = reverse("admin_create_session_type")

    def setUp(self):
        super(AdminTestCase, self).setUp()
        # create an admin user and log them in
        self.password = "password123"
        self.admin = self.db_create_admin(password=self.password)
        self.client.login(username=self.admin.user.username, password=self.password)


class TestListViews(AdminTestCase):


    def setUp(self):
        super(TestListViews, self).setUp()
        # create one of every type of object
        self.db_create_teacher()
        self.db_create_student()

        self.session_type = self.db_create_session_type()
        self.session = self.db_create_session(session_type=self.session_type)

        self.course_type = self.db_create_course_type()
        self.db_create_course(course_type=self.course_type, session=self.session)

    def test_student_list(self):
        response = self.client.get(self.student_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student_list'].count(), 1)

    def test_teacher_list(self):
        response = self.client.get(self.teacher_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['teacher_list'].count(), 1)

    def test_course_list(self):
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['course_list'].count(), 1)

    def test_course_type_list(self):
        response = self.client.get(self.course_type_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['coursetype_list'].count(), 1)

    def test_session_list(self):
        response = self.client.get(self.session_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['session_list'].count(), 1)

    def test_session_type_list(self):
        response = self.client.get(self.session_type_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sessiontype_list'].count(), 1)


class TestCreateViews(AdminTestCase):


    def setUp(self):
        super(TestCreateViews, self).setUp()

    def test_create_student(self):
        self.assertEqual(Student.objects.count(), 0)
        self.assertEqual(User.objects.count(), 1)

        data = {
            "user_form-username": "username",
            "user_form-first_name": "first name",
            "user_form-last_name": "last name",
            "user_form-email": "email@email.com",
            "obj_form-country": self.db_create_country().pk,
            "obj_form-langauge": self.db_create_language().pk,
        }

        response = self.client.post(self.create_student_url, data)
        self.assertRedirects(response, self.student_list_url)
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_create_teacher(self):
        self.assertEqual(Teacher.objects.count(), 0)
        self.assertEqual(User.objects.count(), 1)

        data = {
            "user_form-username": "username",
            "user_form-first_name": "first name",
            "user_form-last_name": "last name",
            "user_form-email": "email@email.com",
        }

        response = self.client.post(self.create_teacher_url, data)
        self.assertRedirects(response, self.teacher_list_url)
        self.assertEqual(Teacher.objects.count(), 1)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_create_course(self):
        self.assertEqual(Course.objects.count(), 0)
        data = {
            "session": self.db_create_session().pk,
            "course_type": self.db_create_course_type().pk,
            "teachers": self.db_create_teacher().pk,
            "students": self.db_create_student().pk,
            "section": 1,
        }
        response = self.client.post(self.create_course_url, data)
        self.assertRedirects(response, self.course_list_url)
        self.assertEqual(Course.objects.count(), 1)

        course = Course.objects.first()
        self.assertEqual(course.teachers.count(), 1)
        self.assertEqual(course.students.count(), 1)

    def test_create_course_type(self):
        self.assertEqual(CourseType.objects.count(), 0)
        data = {
            "institution": self.db_get_or_create_institution().pk,
            "name": "Course Type",
            "verbose_name": "This is the verbose name.",
        }
        response = self.client.post(self.create_course_type_url, data)
        self.assertRedirects(response, self.course_type_list_url)
        self.assertEqual(CourseType.objects.count(), 1)

    def test_create_session(self):
        self.assertEqual(Session.objects.count(), 0)
        data = {
            "session_type": self.db_create_session_type().pk,
            "start_date": "2018-01-01",
            "end_date": "2018-01-01",
        }
        response = self.client.post(self.create_session_url, data)
        self.assertRedirects(response, self.session_list_url)
        self.assertEqual(Session.objects.count(), 1)

    def test_create_session_type(self):
        self.assertEqual(SessionType.objects.count(), 0)
        institution = self.db_get_or_create_institution()
        data = {
            "institution": institution.pk,
            "name": "Session Type",
            "order": "1",
        }
        response = self.client.post(self.create_session_type_url, data)
        self.assertRedirects(response, self.session_type_list_url)
        self.assertEqual(SessionType.objects.count(), 1)









