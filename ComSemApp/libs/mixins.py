from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from ComSemApp.models import Teacher, Worksheet


class RoleViewMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        # is the user an admin, teacher, student?
        role_objects = self.role_class.objects.filter(user=self.request.user)
        if not role_objects.exists():
            return False
        else:
            self.role_obj = role_objects.first()
            self._set_role_obj() # self.admin, teacher, student
            self.institution = self.role_obj.institution
            return True

    def _handle_invalid_course(self):
        invalid_course_string = 'Invalid Course ID'
        if self.request.is_ajax():
            response = JsonResponse({"error": invalid_course_string})
            response.status_code = 403
            return response
        else:
            messages.error(self.request, invalid_course_string)
            return self._get_invalid_course_redirect()

    def _check_valid_worksheet(self, worksheet_id):
        worksheets = Worksheet.objects.filter(id=worksheet_id, course=self.course)
        if not worksheets.exists():
            return False
        return worksheets.first()

    def _handle_invalid_worksheet(self):
        invalid_worksheet_string = 'Invalid Worksheet ID'
        if self.request.is_ajax():
            response = JsonResponse({"error": invalid_worksheet_string})
            response.status_code = 403
            return response
        else:
            messages.error(self.request, invalid_worksheet_string)
            return self._get_invalid_worksheet_redirect()


class CourseViewMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # is the user a teacher / student for this course ?
        course_id = kwargs.get('course_id', None)
        self.course = self._check_valid_course(course_id)
        if not self.course:
            return self._handle_invalid_course()
        return super(CourseViewMixin, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseViewMixin, self).get_context_data(**kwargs)
        context['course'] = self.course
        return context


class WorksheetViewMixin(object):

    def dispatch(self, request, *args, **kwargs):
        # is the user a teacher / teacher for this course ?
        course_id = kwargs.get('course_id', None)
        self.course = self._check_valid_course(course_id)
        if not self.course:
            return self._handle_invalid_course()

        # is the worksheet valid for this course ?
        worksheet_id = kwargs.get('worksheet_id', None)
        self.worksheet = self._check_valid_worksheet(worksheet_id)
        if not self.worksheet:
            return self._handle_invalid_worksheet()
        return super(WorksheetViewMixin, self).dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(WorksheetViewMixin, self).get_context_data(**kwargs)
        context['course'] = self.course
        context['worksheet'] = self.worksheet
        return context