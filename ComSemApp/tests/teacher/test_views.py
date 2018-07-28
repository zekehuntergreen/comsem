from django.urls import reverse
from django.core import mail

from ComSemApp.tests import BaseTestCase
from ComSemApp.models import *


class TestCredentials(BaseTestCase):
    # only admin users should be able to access admin views.

    teacher_home_url = reverse("teacher")
    loggin_url = reverse("login")

    def setUp(self):
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