from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail

from ComSemApp.libs.factories import BaseTestCase
from ComSemApp.models import *


class TestCredentials(BaseTestCase):
    # only admin users should be able to access admin views.

    teacher_list_url = reverse("admin:teachers")
    loggin_url = reverse("login")

    def setUp(self):
        super(TestCredentials, self).setUp()
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


class AdminTestCase(object):
    # base test case mixin for all admin views. tests list, create, update, delete

    def setUp(self):
        # create an admin user and log them in
        self.password = "password123"
        self.admin = self.db_create_admin(password=self.password)
        self.client.login(username=self.admin.user.username, password=self.password)

    def test_list_view(self):
        self.create_object()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context[self.list_prefix + '_list'].count(), 1)

    def test_create_view(self):
        # get
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)

        # post
        self.assertEqual(self.obj.objects.count(), 0)
        response = self.client.post(self.create_url, self.get_data())
        self.assertRedirects(response, self.list_url)
        self.assertEqual(self.obj.objects.count(), 1)

    def test_update_view(self):
        # get
        obj = self.create_object()
        update_url = reverse(self.update_url_string, kwargs={"pk": obj.pk})
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

        # post
        response = self.client.post(update_url, self.get_data())
        self.assertRedirects(response, self.list_url)

    def test_delete_view(self):
        obj = self.create_object()
        self.assertEqual(self.obj.objects.count(), 1)
        delete_url = reverse(self.delete_url_string, kwargs={"pk": obj.pk})
        response = self.client.get(delete_url)
        self.assertRedirects(response, self.list_url)
        self.assertEqual(self.obj.objects.count(), 0)

    def _test_delete_view_user_obj(self):
        # for teacher and student objects - we disactivate rather than delete
        obj = self.create_object()
        self.assertEqual(self.obj.objects.count(), 1)
        self.assertEqual(self.obj.objects.first().user.is_active, True)
        delete_url = reverse(self.delete_url_string, kwargs={"pk": obj.pk})
        response = self.client.get(delete_url)
        self.assertRedirects(response, self.list_url)
        self.assertEqual(self.obj.objects.count(), 1)
        self.assertEqual(self.obj.objects.first().user.is_active, False)


class TestStudentViews(AdminTestCase, BaseTestCase):
    obj = Student
    list_url = reverse("admin:students")
    create_url = reverse("admin:create_student")
    update_url_string = "admin:edit_student"
    delete_url_string = "admin:disactivate_student"
    list_prefix = "student"

    def setUp(self):
        super(TestStudentViews, self).setUp()
        self.create_object = self.db_create_student

    def test_create_view(self):
        # override in order to do extra checks
        super(TestStudentViews, self).test_create_view()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_delete_view(self):
        # override delete tests - we are disactivating instead
        self._test_delete_view_user_obj()

    def get_data(self):
        return {
            "user_form-username": "username",
            "user_form-first_name": "first name",
            "user_form-last_name": "last name",
            "user_form-email": "email@email.com",
            "obj_form-country": self.db_create_country().pk,
            "obj_form-langauge": self.db_create_language().pk,
        }


class TestTeacherViews(AdminTestCase, BaseTestCase):
    obj = Teacher
    list_url = reverse("admin:teachers")
    create_url = reverse("admin:create_teacher")
    update_url_string = "admin:edit_teacher"
    delete_url_string = "admin:disactivate_teacher"
    list_prefix = "teacher"

    def setUp(self):
        super(TestTeacherViews, self).setUp()
        self.create_object = self.db_create_teacher

    def test_create_view(self):
        # override in order to do extra checks
        super(TestTeacherViews, self).test_create_view()
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 1)

    def test_delete_view(self):
        # override delete tests - we are disactivating instead
        self._test_delete_view_user_obj()

    def get_data(self):
        return {
            "user_form-username": "username",
            "user_form-first_name": "first name",
            "user_form-last_name": "last name",
            "user_form-email": "email@email.com",
        }


class TestCourseViews(AdminTestCase, BaseTestCase):
    obj = Course
    list_url = reverse("admin:courses")
    create_url = reverse("admin:create_course")
    update_url_string = "admin:edit_course"
    delete_url_string = "admin:delete_course"
    list_prefix = "course"

    def setUp(self):
        super(TestCourseViews, self).setUp()
        self.create_object = self.db_create_course

    def get_data(self):
        return {
            "session": self.db_create_session().pk,
            "course_type": self.db_create_course_type().pk,
            "teachers": self.db_create_teacher().pk,
            "students": self.db_create_student().pk,
            "section": 1,
        }


class TestCourseTypeViews(AdminTestCase, BaseTestCase):
    obj = CourseType
    list_url = reverse("admin:course_types")
    create_url = reverse("admin:create_course_type")
    update_url_string = "admin:edit_course_type"
    delete_url_string = "admin:delete_course_type"
    list_prefix = "coursetype"

    def setUp(self):
        super(TestCourseTypeViews, self).setUp()
        self.create_object = self.db_create_course_type

    def get_data(self):
        return {
            "institution": self.db_get_or_create_institution().pk,
            "name": "Course Type",
            "verbose_name": "This is the verbose name.",
        }


class TestSessionViews(AdminTestCase, BaseTestCase):
    obj = Session
    list_url = reverse("admin:sessions")
    create_url = reverse("admin:create_session")
    update_url_string = "admin:edit_session"
    delete_url_string = "admin:delete_session"
    list_prefix = "session"

    def setUp(self):
        super(TestSessionViews, self).setUp()
        self.create_object = self.db_create_session

    def get_data(self):
        return {
            "session_type": self.db_create_session_type().pk,
            "start_date": "2018-01-01",
            "end_date": "2018-01-01",
        }


class TestSessionTypeViews(AdminTestCase, BaseTestCase):
    obj = SessionType
    list_url = reverse("admin:session_types")
    create_url = reverse("admin:create_session_type")
    update_url_string = "admin:edit_session_type"
    delete_url_string = "admin:delete_session_type"
    list_prefix = "sessiontype"

    def setUp(self):
        super(TestSessionTypeViews, self).setUp()
        self.create_object = self.db_create_session_type

    def get_data(self):
        return {
            "institution": self.db_get_or_create_institution().pk,
            "name": "Session Type",
            "order": "1",
        }
