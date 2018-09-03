from django.urls import reverse
from django.core import mail

from ComSemApp.libs.factories import BaseTestCase
from ComSemApp.models import *

from ComSemApp.teacher.constants import WORKSHEET_STATUS_PENDING, WORKSHEET_STATUS_UNRELEASED, WORKSHEET_STATUS_RELEASED


class TestCredentials(BaseTestCase):
    # only students should be able to access students views.

    student_home_url = reverse("student:courses")
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
        self.unenrolled_course = self.db_create_course()
        self.unreleased_worksheet = self.db_create_worksheet(course=self.course)
        self.released_worksheet = self.db_create_worksheet(course=self.course, status=WORKSHEET_STATUS_RELEASED)


class TestCourseListView(TestStudentMixin):

    def test_success(self):
        response = self.client.get(reverse("student:courses"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.course, response.context['courses'])

    def test_unenrolled_not_in_list(self):
        response = self.client.get(reverse("student:courses"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.unenrolled_course, response.context['courses'])


class TestCourseViewMixin(TestStudentMixin):

    def test_invalid_course_fail(self):
        response = self.client.get(reverse("student:course", kwargs={'course_id': 100}), follow=True)
        self.assertRedirects(response, reverse("student:courses"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")

    def test_invalid_teacher_fail(self):
        course = self.db_create_course()
        response = self.client.get(reverse("student:course", kwargs={'course_id': course.id}), follow=True)
        self.assertRedirects(response, reverse("student:courses"))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Invalid Course ID")


class TestCourseDetailView(TestStudentMixin):

    def test_success(self):
        worksheet_in_unenrolled_course = self.db_create_worksheet(course=self.unenrolled_course)

        response = self.client.get(reverse("student:course", kwargs={'course_id': self.course.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['course'], self.course)

        # don't show unreleased worksheets or worksheets from other courses
        self.assertIn(self.released_worksheet, response.context['worksheets'])
        self.assertNotIn(self.unreleased_worksheet, response.context['worksheets'])
        self.assertNotIn(worksheet_in_unenrolled_course, response.context['worksheets'])


class TestSubmissionListView(TestStudentMixin):

    def test_success(self):
        my_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet)
        another_student = self.db_create_student()
        another_students_submission = self.db_create_submission(student=another_student, worksheet=self.released_worksheet)
        response = self.client.get(reverse("student:submission_list",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(my_submission, response.context['submissions'])
        self.assertNotIn(another_students_submission, response.context['submissions'])


class TestCreateSubmissionView(TestStudentMixin):

    def test_get_success(self):
        # pending submission created
        self.assertEqual(self.released_worksheet.submissions.count(), 0)
        response = self.client.get(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.released_worksheet.submissions.count(), 1)
        self.assertEqual(self.released_worksheet.submissions.first().status, "pending")

    def test_get_pending_exists_success(self):
        # existing pending submission used
        pending_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="pending")
        self.assertEqual(self.released_worksheet.submissions.count(), 1)

        response = self.client.get(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.released_worksheet.submissions.count(), 1)
        self.assertEqual(response.context['submission'], pending_submission)

    def test_incomplete_exists_success(self):
        pending_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="incomplete")
        self.assertEqual(self.released_worksheet.submissions.count(), 1)
        response = self.client.get(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.released_worksheet.submissions.count(), 2)
        self.assertEqual(response.context['submission'].status, "pending")

    def test_ungraded_exists_redirect(self):
        pending_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="ungraded")
        response = self.client.get(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}), follow=True)
        self.assertRedirects(response, reverse("student:course", kwargs={'course_id': self.course.id}))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "You may not create a submission for this worksheet.")

    def test_complete_exists_redirect(self):
        pending_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="complete")
        response = self.client.get(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}), follow=True)
        self.assertRedirects(response, reverse("student:course", kwargs={'course_id': self.course.id}))
        self.assertEqual(str(list(response.context.get('messages'))[0]), "You may not create a submission for this worksheet.")

    def test_post_success(self):
        response = self.client.get(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}))
        self.assertEqual(response.status_code, 200)
        submission = self.released_worksheet.submissions.first()

        response = self.client.post(reverse("student:create_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id}), follow=True)
        self.assertRedirects(response, reverse("student:course", kwargs={'course_id': self.course.id}))
        submission.refresh_from_db()
        self.assertEqual(submission.status, "ungraded")
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Submission successful")


class TestCreateSubmissionView(TestStudentMixin):

    def test_last_submission_ungraded_get_success(self):
        ungraded_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="ungraded")
        response = self.client.get(reverse("student:update_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id, 'submission_id': ungraded_submission.id}))
        self.assertEqual(response.status_code, 200)

    def test_last_submission_not_ungraded_404(self):
        # pending
        pending_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="pending")
        response = self.client.get(reverse("student:update_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id, 'submission_id': pending_submission.id}))
        self.assertEqual(response.status_code, 404)

        # complete
        complete_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="complete")
        response = self.client.get(reverse("student:update_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id, 'submission_id': complete_submission.id}))
        self.assertEqual(response.status_code, 404)

        # complete
        incomplete_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="incomplete")
        response = self.client.get(reverse("student:update_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id, 'submission_id': incomplete_submission.id}))
        self.assertEqual(response.status_code, 404)

    def test_post_success(self):
        ungraded_submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet, status="ungraded")
        response = self.client.post(reverse("student:update_submission",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id, 'submission_id': ungraded_submission.id}), follow=True)
        self.assertRedirects(response, reverse("student:course", kwargs={'course_id': self.course.id}))
        # no change to db
        self.assertEqual(str(list(response.context.get('messages'))[0]), "Submission updated")


class TestSubmissionsMixin(TestStudentMixin):

    def setUp(self):
        super(TestSubmissionsMixin, self).setUp()
        self.expression_1 = self.db_create_expression(worksheet=self.released_worksheet)
        self.expression_2 = self.db_create_expression(worksheet=self.released_worksheet)
        self.submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet)

class TestExpressionListView(TestSubmissionsMixin):

    def test_get_success(self):
        response = self.client.get(reverse("student:worksheet_expression_list",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id, 'submission_id': self.submission.id}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.expression_1, response.context['expressions'])
        self.assertIn(self.expression_2, response.context['expressions'])


class TestAttemptCreateView(TestSubmissionsMixin):

    def test_get_success(self):
        response = self.client.get(reverse("student:create_attempt",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id,
                        'submission_id': self.submission.id, 'expression_id': self.expression_1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['expression'], self.expression_1)

    def test_get_bad_expression_fail(self):
        expression_3 = self.db_create_expression(worksheet=self.unreleased_worksheet)
        response = self.client.get(reverse("student:create_attempt",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id,
                        'submission_id': self.submission.id, 'expression_id': expression_3.id}))
        self.assertEqual(response.status_code, 404)

    def test_post_success(self):
        self.assertEqual(self.submission.attempts.count(), 0)
        reformulation_text = "this is the reformulation text!"
        post_data = {
            "reformulation_text": reformulation_text,
            "reformulation_audio": False,
            # TODO: test this !
        }
        response = self.client.post(reverse("student:create_attempt",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id,
                        'submission_id': self.submission.id, 'expression_id': self.expression_1.id}), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.submission.attempts.count(), 1)
        self.assertEqual(self.submission.attempts.first().reformulation_text, reformulation_text)


class TestAttemptUpdateView(TestSubmissionsMixin):

    def setUp(self):
        super(TestAttemptUpdateView, self).setUp()
        self.submission = self.db_create_submission(student=self.student, worksheet=self.released_worksheet)
        self.expression_1 = self.db_create_expression(worksheet=self.released_worksheet)
        self.attempt = self.db_create_attempt(expression=self.expression_1, submission=self.submission)

    def test_get_success(self):
        response = self.client.get(reverse("student:update_attempt",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id,
                        'submission_id': self.submission.id, 'attempt_id': self.attempt.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['expression'], self.expression_1)
        self.assertEqual(response.context['attempt'], self.attempt)

    def test_post_success(self):
        self.assertEqual(self.submission.attempts.count(), 1)
        reformulation_text = "this is the UPDATED reformulation text!"
        post_data = {
            "reformulation_text": reformulation_text,
            "reformulation_audio": False,
            # TODO: test this !
        }
        response = self.client.post(reverse("student:update_attempt",
                kwargs={'course_id': self.course.id, 'worksheet_id': self.released_worksheet.id,
                        'submission_id': self.submission.id, 'attempt_id': self.attempt.id}), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.submission.attempts.count(), 1)
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.reformulation_text, reformulation_text)

