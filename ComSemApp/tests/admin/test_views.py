from ComSemApp.tests import BaseTestCase
from django.urls import reverse

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








