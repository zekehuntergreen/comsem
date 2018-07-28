from django.urls import reverse
from django.core import mail

from ComSemApp.tests import BaseTestCase
from ComSemApp.models import *


class TestCredentials(BaseTestCase):
    # only teachers should be able to access teacher views.

    teacher_home_url = reverse("teacher")
    loggin_url = reverse("login")

    def setUp(self):
        super(TestCredentials, self).setUp()
        self.password = "password123"
        self.teacher = self.db_create_teacher(password=self.password)
        self.student = self.db_create_student(password=self.password)

    def test_not_logged_in_fail(self):
        response = self.client.get(self.teacher_home_url)
        self.assertRedirects(response, '%s?next=%s' % (self.loggin_url, self.teacher_home_url))

    def test_logged_in_not_teacher_fail(self):
        self.client.login(username=self.student.user.username, password=self.password)
        response = self.client.get(self.teacher_home_url)
        # TODO: should we be doing something else here? 404? redirect to teacher home?
        self.assertRedirects(response, '%s?next=%s' % (self.loggin_url, self.teacher_home_url))

    def test_logged_in_teacher_success(self):
        self.client.login(username=self.teacher.user.username, password=self.password)
        response = self.client.get(self.teacher_home_url)
        self.assertEqual(response.status_code, 200)


class TestTeacherMixin(BaseTestCase):

    def setUp(self):
        super(TestTeacherMixin, self).setUp()
        self.password = "password123"
        self.teacher = self.db_create_teacher(password=self.password)
        self.client.login(username=self.teacher.user.username, password=self.password)

        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)


class TestCourseListView(TestTeacherMixin):

    def test_success(self):
        response = self.client.get(reverse("teacher"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['courses'].first(), self.course)


class TestCourseDetailView(TestTeacherMixin):

    def test_success(self):
        response = self.client.get(reverse("teacher"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['course'], self.course)

