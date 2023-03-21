from django.urls import reverse
from django.core import mail

from ComSemApp.libs.factories import BaseTestCase
from ComSemApp.models import *

from ComSemApp.teacher.constants import WORKSHEET_STATUS_PENDING, WORKSHEET_STATUS_UNRELEASED, WORKSHEET_STATUS_RELEASED


class TestCredentials(BaseTestCase):
    # only teachers should be able to access teacher views.

    teacher_home_url = reverse("teacher:courses")
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
        self.assertEqual(response.status_code, 403)

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


class TestCourseListView(TestTeacherMixin):

    def test_success(self):
        course = self.db_create_course()
        course.teachers.add(self.teacher)

        response = self.client.get(reverse("teacher:courses"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['courses'].first(), course)


class TestCourseViewMixin(TestTeacherMixin):

    def test_invalid_course_fail(self):
        response = self.client.get(reverse("teacher:course", kwargs={'course_id': 100}), follow=True)
        self.assertRedirects(response, reverse("teacher:courses"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")

    def test_invalid_teacher_fail(self):
        course = self.db_create_course()
        response = self.client.get(reverse("teacher:course", kwargs={'course_id': course.id}), follow=True)
        self.assertRedirects(response, reverse("teacher:courses"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")


class TestCourseDetailView(TestTeacherMixin):

    def test_success(self):
        course = self.db_create_course()
        course.teachers.add(self.teacher)

        response = self.client.get(reverse("teacher:course", kwargs={'course_id': course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['course'], course)


class TestWorksheetListView(TestTeacherMixin):

    def setUp(self):
        super(TestWorksheetListView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)

    def test_get_success(self):
        response = self.client.get(reverse("teacher:worksheet_list", kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['worksheets'].first(), self.worksheet)


class TestWorksheetCreateView(TestTeacherMixin):

    def setUp(self):
        super(TestWorksheetCreateView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)

    def test_get_success(self):
        self.assertEqual(Worksheet.objects.all().count(), 0)
        response = self.client.get(reverse("teacher:worksheet_create", kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Worksheet.objects.all().count(), 1)

        worksheet = Worksheet.objects.first()
        self.assertEqual(worksheet.status, WORKSHEET_STATUS_PENDING)
        self.assertEqual(worksheet.created_by, self.teacher)
        self.assertEqual(worksheet.course, self.course)

    def test_post_success(self):
        post_data = {
            'topic': 'This is the topic!',
            'display_original': True,
            'display_reformulation_text': True,
            'display_reformulation_audio': True,
            'display_all_expressions': True,
        }
        response = self.client.post(reverse("teacher:worksheet_create", kwargs={'course_id': self.course.id}), data=post_data)
        self.assertRedirects(response, reverse("teacher:course", kwargs={'course_id': self.course.id}))

        worksheet = Worksheet.objects.first()
        worksheet.refresh_from_db()
        self.assertEqual(worksheet.status, WORKSHEET_STATUS_UNRELEASED)
        self.assertEqual(worksheet.topic, 'This is the topic!')
        self.assertEqual(worksheet.display_original, True)
        self.assertEqual(worksheet.display_reformulation_text, True)
        self.assertEqual(worksheet.display_reformulation_audio, True)
        self.assertEqual(worksheet.display_all_expressions, True)


class TestWorksheetViewMixin(TestTeacherMixin):

    def test_invalid_course_fail(self):
        response = self.client.get(reverse("teacher:course", kwargs={'course_id': 100}), follow=True)
        self.assertRedirects(response, reverse("teacher:courses"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")

    def test_invalid_teacher_fail(self):
        course = self.db_create_course()
        response = self.client.get(reverse("teacher:course", kwargs={'course_id': course.id}), follow=True)
        self.assertRedirects(response, reverse("teacher:courses"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")

    def test_invalid_worksheet_fail(self):
        course = self.db_create_course()
        course.teachers.add(self.teacher)

        response = self.client.get(reverse("teacher:worksheet_update",
                kwargs={'course_id': course.id, 'worksheet_id': 100}), follow=True)
        self.assertRedirects(response, reverse("teacher:course", kwargs={'course_id': course.id}))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Worksheet ID")

    def test_worksheet_not_in_course_fail(self):
        course_1 = self.db_create_course()
        course_1.teachers.add(self.teacher)
        course_2 = self.db_create_course()
        course_2.teachers.add(self.teacher)

        worksheet = self.db_create_worksheet(course=course_2)

        response = self.client.get(reverse("teacher:worksheet_update",
                kwargs={'course_id': course_1.id, 'worksheet_id': worksheet.id}), follow=True)
        self.assertRedirects(response, reverse("teacher:course", kwargs={'course_id': course_1.id}))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Worksheet ID")


class TestWorksheetUpdateView(TestTeacherMixin):

    def setUp(self):
        super(TestWorksheetUpdateView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)

    def test_get_success(self):
        response = self.client.get(reverse("teacher:worksheet_update",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        post_data = {
            'topic': 'New Topic',
            'display_original': False,
            'display_reformulation_text': False,
            'display_reformulation_audio': False,
            'display_all_expressions': False,
        }
        response = self.client.post(reverse("teacher:worksheet_update",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}), data=post_data)
        self.assertRedirects(response, reverse("teacher:course", kwargs={'course_id': self.course.id}))

        worksheet = Worksheet.objects.first()
        worksheet.refresh_from_db()
        self.assertEqual(worksheet.status, WORKSHEET_STATUS_UNRELEASED)
        self.assertEqual(worksheet.topic, 'New Topic')
        self.assertEqual(worksheet.display_original, False)
        self.assertEqual(worksheet.display_reformulation_text, False)
        self.assertEqual(worksheet.display_reformulation_audio, False)
        self.assertEqual(worksheet.display_all_expressions, False)


class TestWorksheetReleaseView(TestTeacherMixin):

    def setUp(self):
        super(TestWorksheetReleaseView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)

    def test_post_success(self):
        self.db_create_expression(worksheet=self.worksheet)

        self.assertEqual(self.worksheet.status, WORKSHEET_STATUS_UNRELEASED)
        response = self.client.post(reverse("teacher:worksheet_release",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.assertEqual(response.status_code, 204)
        self.worksheet.refresh_from_db()
        self.assertEqual(self.worksheet.status, WORKSHEET_STATUS_RELEASED)

    def test_cannot_release_empty_worksheet(self):
        self.assertEqual(self.worksheet.status, WORKSHEET_STATUS_UNRELEASED)
        response = self.client.post(reverse("teacher:worksheet_release",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.assertEqual(response.reason_phrase, "Worksheet must have at least one expression with a reforumlation.")
        self.assertEqual(response.status_code, 406)
        self.worksheet.refresh_from_db()
        self.assertEqual(self.worksheet.status, WORKSHEET_STATUS_UNRELEASED)


class TestWorksheetDeleteView(TestTeacherMixin):

    def setUp(self):
        super(TestWorksheetDeleteView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)

    def test_post_success(self):
        response = self.client.post(reverse("teacher:worksheet_delete",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Worksheet.objects.count(), 0)


class TestExpressionListView(TestTeacherMixin):

    def setUp(self):
        super(TestExpressionListView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)
        self.expression = self.db_create_expression(worksheet=self.worksheet)

    def test_success(self):
        response = self.client.get(reverse("teacher:expressions", kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['expressions'].first(), self.expression)


class TestExpressionCreateView(TestTeacherMixin):

    def setUp(self):
        super(TestExpressionCreateView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)

    def test_get_success(self):
        response = self.client.get(reverse("teacher:expression_create",
            kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        self.assertEqual(Expression.objects.all().count(), 0)
        student = self.db_create_student()
        post_data = {
            "expression": "Expression",
            "student": student.id,
            "all_do": True,
            "pronunciation": "P",
            "context_vocabulary": "C",
            "reformulation_text": "R",
            # "audio": None,
            # TODO test audio upload
        }
        response = self.client.post(reverse("teacher:expression_create",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}), data=post_data)
        self.assertEqual(Expression.objects.all().count(), 1)

        expression = Expression.objects.first()
        self.assertEqual(expression.expression, "Expression")
        self.assertEqual(expression.student, student)
        self.assertEqual(expression.all_do, True)
        self.assertEqual(expression.pronunciation, "P")
        self.assertEqual(expression.context_vocabulary, "C")
        self.assertEqual(expression.reformulation_text, "R")
        self.assertFalse(expression.audio)


class TestExpressionUpdateView(TestTeacherMixin):

    def setUp(self):
        super(TestExpressionUpdateView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)
        self.expression = self.db_create_expression(worksheet=self.worksheet)

    def test_get_success(self):
        response = self.client.get(reverse("teacher:expression_update",
            kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id, 'expression_id': self.expression.id}))
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        student = self.db_create_student()
        post_data = {
            "expression": "Expression",
            "student": student.id,
            "all_do": True,
            "pronunciation": "P",
            "context_vocabulary": "C",
            "reformulation_text": "R",
            # "audio": None,
            # TODO test audio upload
        }
        response = self.client.post(reverse("teacher:expression_update",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id, 'expression_id': self.expression.id}), data=post_data)

        expression = Expression.objects.first()
        self.assertEqual(expression.expression, "Expression")
        self.assertEqual(expression.student, student)
        self.assertEqual(expression.all_do, True)
        self.assertEqual(expression.pronunciation, "P")
        self.assertEqual(expression.context_vocabulary, "C")
        self.assertEqual(expression.reformulation_text, "R")
        self.assertFalse(expression.audio)


class TestExpressionDeleteView(TestTeacherMixin):

    def setUp(self):
        super(TestExpressionDeleteView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)
        self.expression = self.db_create_expression(worksheet=self.worksheet)

    def test_success(self):
        self.assertEqual(Expression.objects.all().count(), 1)
        response = self.client.post(reverse("teacher:expression_delete",
            kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id, 'expression_id': self.expression.id}))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Expression.objects.all().count(), 0)


class TestSubmissionView(TestTeacherMixin):

    def setUp(self):
        super(TestSubmissionView, self).setUp()
        self.course = self.db_create_course()
        self.course.teachers.add(self.teacher)
        self.worksheet = self.db_create_worksheet(course=self.course)
        self.expression_1 = self.db_create_expression(worksheet=self.worksheet)
        self.expression_2 = self.db_create_expression(worksheet=self.worksheet)
        self.submission = self.db_create_submission(worksheet=self.worksheet, status='ungraded')
        self.attempt_1 = self.db_create_attempt(submission=self.submission, expression=self.expression_1)
        self.attempt_2 = self.db_create_attempt(submission=self.submission, expression=self.expression_2)

    def test_get_success(self):
        response = self.client.get(reverse("teacher:submission",
            kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id, 'submission_id': self.submission.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['submission'], self.submission)

    def test_post_success(self):
        self.assertEqual(self.submission.status, "ungraded")
        # mark incomplete
        post_data = {
            "T" + str(self.attempt_1.id): "1",
            "T" + str(self.attempt_2.id): "0",
        }
        response = self.client.post(reverse("teacher:submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id, 'submission_id': self.submission.id}), data=post_data)
        self.assertRedirects(response, reverse("teacher:worksheet_detail",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "incomplete")

        # mark complete
        post_data = {
            "T" + str(self.attempt_1.id): "1",
            "T" + str(self.attempt_2.id): "1",
        }
        response = self.client.post(reverse("teacher:submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id, 'submission_id': self.submission.id}), data=post_data)
        self.assertRedirects(response, reverse("teacher:worksheet_detail",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.worksheet.id}))
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "complete")
