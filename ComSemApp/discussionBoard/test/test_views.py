from django.urls import reverse
from django.core import mail

from ComSemApp.libs.factories import BaseTestCase
from ComSemApp.models import *

class TestCredentials(BaseTestCase):

    # only students and teachers should be able to access students views.

    discussion_board_url = reverse("discussion_board:topics")
    loggin_url = reverse("login")

    def setUp(self):
        super(TestCredentials, self).setUp()
        self.password = "password123"
        self.teacher = self.db_create_teacher(password=self.password)
        self.student = self.db_create_student(password=self.password)

    def test_not_logged_in_fail(self):
        response = self.client.get(self.discussion_board_url)
        self.assertRedirects(response, '%s?next=%s' % (self.login_url, self.discussion_board_url))

    def test_logged_in_teacher_success(self):
        self.client.login(username=self.teacher.user.username, password=self.password)
        response = self.client.get(self.discussion_board_url)
        self.assertEqual(response.status_code, 200)

    def test_logged_in_student_success(self):
        self.client.login(username=self.student.user.username, password=self.password)
        response = self.client.get(self.discussion_board_url)
        self.assertEqual(response.status_code, 200)
