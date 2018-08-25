from django.urls import reverse
from django.core import mail

from ComSemApp.tests import BaseTestCase
from ComSemApp.models import *

from ComSemApp.teacher_constants import WORKSHEET_STATUS_PENDING, WORKSHEET_STATUS_UNRELEASED, WORKSHEET_STATUS_RELEASED


class TestCredentials(BaseTestCase):
    # only students should be able to access students views.

    student_home_url = reverse("student")
    loggin_url = reverse("login")

    def setUp(self):
        super(TestCredentials, self).setUp()
        self.password = "password123"
        self.teacher = self.db_create_teacher(password=self.password)
        self.student = self.db_create_student(password=self.password)

    def test_not_logged_in_fail(self):
        response = self.client.get(self.student_home_url)
        self.assertRedirects(response, '%s?next=%s' % (self.loggin_url, self.student_home_url))

    def test_logged_in_not_student_fail(self):
        self.client.login(username=self.teacher.user.username, password=self.password)
        response = self.client.get(self.student_home_url)
        # TODO: should we be doing something else here? 404? redirect to student home?
        self.assertRedirects(response, '%s?next=%s' % (self.loggin_url, self.student_home_url))

    def test_logged_in_student_success(self):
        self.client.login(username=self.student.user.username, password=self.password)
        response = self.client.get(self.student_home_url)
        self.assertEqual(response.status_code, 200)


class TestStudentMixin(BaseTestCase):

    def setUp(self):
        super(TestStudentMixin, self).setUp()
        self.password = "password123"
        self.student = self.db_create_student(password=self.password)
        self.client.login(username=self.student.user.username, password=self.password)

        self.course = self.db_create_course()
        self.course.students.add(self.student)
        self.worksheet = self.db_create_worksheet(course=self.course)


class TestCourseListView(TestStudentMixin):

    def test_success(self):
        response = self.client.get(reverse("student"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['courses'].first(), self.course)


class TestCourseViewMixin(TestStudentMixin):

    def test_invalid_course_fail(self):
        response = self.client.get(reverse("student_course", kwargs={'course_id': 100}), follow=True)
        self.assertRedirects(response, reverse("student"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")

    def test_invalid_teacher_fail(self):
        course = self.db_create_course()
        response = self.client.get(reverse("student_course", kwargs={'course_id': course.id}), follow=True)
        self.assertRedirects(response, reverse("student"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")



class TestCourseDetailView(TestStudentMixin):

    def test_success(self):
        response = self.client.get(reverse("student_course", kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['course'], self.course)
        self.assertEqual(response.context['worksheets'][0], self.worksheet)

