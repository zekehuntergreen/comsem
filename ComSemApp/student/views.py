import json

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.test import Client
from ComSemApp.teacher.constants import WORKSHEET_STATUS_PENDING, WORKSHEET_STATUS_UNRELEASED, WORKSHEET_STATUS_RELEASED
import datetime

from ComSemApp.teacher import constants as teacher_constants

from ComSemApp.models import *
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin, SubmissionViewMixin

class StudentViewMixin(RoleViewMixin):

    role_class = Student

    def _set_role_obj(self):
        # role_obj self in RoleViewMixin
        self.student = self.role_obj

    def _check_valid_course(self, course_id):
        courses = Course.objects.filter(students=self.request.user.student, id=course_id)
        if not courses.exists():
            return False
        return courses.first()


class StudentCourseViewMixin(StudentViewMixin, CourseViewMixin):

    def _get_invalid_course_redirect(self):
        return HttpResponseRedirect(reverse("student:courses"))


class StudentWorksheetViewMixin(StudentViewMixin, WorksheetViewMixin):

    def _get_invalid_worksheet_redirect(self):
        return HttpResponseRedirect(reverse("student:course", kwargs={"course_id": self.course.id}))


class StudentSubmissionViewMixin(StudentViewMixin, SubmissionViewMixin):

    def _get_invalid_submission_redirect(self):
        return HttpResponseRedirect(reverse("student:course", kwargs={"course_id": self.course.id}))


class CourseListView(StudentViewMixin, ListView):
    # student home page
    model = Course
    template_name = 'ComSemApp/student/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(students=self.student)


class CourseDetailView(StudentCourseViewMixin, DetailView):
    context_object_name = 'course'
    template_name = "ComSemApp/student/course.html"

    def post(self, request, *args, **kwargs): #create Worksheets
        self.generate_worksheet()


        return HttpResponseRedirect(reverse("student:course", kwargs={"course_id": self.course.id}))


    def db_create_expression(self, worksheet, student, expression):

        defaults = {
            "worksheet": worksheet,
            "expression": expression.expression,
            "student": student,
            "all_do": False,
            "pronunciation": expression.pronunciation,
            "context_vocabulary": expression.context_vocabulary,
            "reformulation_text": expression.reformulation_text,
            "audio": expression.audio,
        }
        return Expression.objects.create(**defaults)

    def create_worksheet(self, **kwargs):
        course = kwargs.get("course")
        if not course:
            course = self.db_create_course()

        defaults = {
            "course": course,
            "topic": kwargs.get("topic", "TOPIC"),
            "status": kwargs.get("status", WORKSHEET_STATUS_UNRELEASED),
            "display_original": kwargs.get("display_original", True),
            "display_reformulation_text": kwargs.get("display_reformulation_text", True),
            "display_reformulation_audio": kwargs.get("display_reformulation_audio", True),
            "display_all_expressions": kwargs.get("display_all_expressions", True),
            "autogen": True,
            "auto_student": self.student
        }

        return Worksheet.objects.create(**defaults)

    def get_object(self):
        return self.course

    # Generates a practice worksheet for a student
    def generate_worksheet(self, **kwargs):

        worksheets = self.course.worksheets
        worksheets.filter(Q(auto_student=self.student) | Q(auto_student=None), status=teacher_constants.WORKSHEET_STATUS_RELEASED)
        expressions = ""
        expressionList = []
        get_top = []  # Most attempted worksheets and attempts tuple
        top_worksheets = []  # Most attempted worksheets
        top_expressions = []  # Expressions from most attempted worksheets



        # make a list of worksheets with most attempts
        for worksheet in worksheets.all():
            if worksheet.auto_student == self.student or worksheet.auto_student == None:
                print('fklnjsdfsdklj')
                print(worksheet.auto_student)
                # get the last submission on the worksheet
                # assign that submission to a variable, then run .get_number() on that
                # keep track of the highest 3 worksheets
                last_sub = worksheet.last_submission(self.student)
                attempts = 0
                if last_sub:
                    attempts = last_sub.get_number()

                    get_top.append((worksheet, attempts)) #str worksheet is the ID






        # # Sort and keep top 3 most attempted worksheets
        top_worksheets = sorted(get_top, key=lambda tup: tup[1], reverse=True)[:3]
        top_worksheets = [i[0] for i in top_worksheets]


        # Get expressions from top worksheets
        for worksheet in top_worksheets:
            print("HERHHERHEHEHR")
            print(worksheet)

            # change current worksheet to a string to compare to the list
            expression_filters = Q(Q(student=self.student) | Q(student=None) | Q(all_do=True) | Q(worksheet=worksheet))
            expressions = Expression.objects.filter(expression_filters)




            # If current worksheet is in top list add it's expressions to top_expressions
            for expression in expressions:
                if expression.worksheet in top_worksheets:
                    top_expressions.append(expression)

        # create worksheet with unique name based on current time

        print("TOP EXPRESSIONS")
        print(top_expressions)




        current_time = datetime.datetime.now()
        new_topic = str("Practice Worksheet " + current_time.strftime("%Y-%m-%d %H:%M:%S") + " for " + self.student.user.first_name + " " + self.student.user.last_name)
        defaults = {
            "course": self.course,
            "topic": new_topic,
            "status": kwargs.get("status", WORKSHEET_STATUS_UNRELEASED),
            "display_original": kwargs.get("display_original", True),
            "display_reformulation_text": kwargs.get("display_reformulation_text", True),
            "display_reformulation_audio": kwargs.get("display_reformulation_audio", True),
            "display_all_expressions": kwargs.get("display_all_expressions", True),
            "auto_student": self.student,
            "autogen": True
        }

        self.create_worksheet(**defaults)

        # assign newly created worksheet to autogen_worksheet variable
        for worksheet in self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_UNRELEASED).all():
            print(worksheets)
            topic_check = str(worksheet.topic)
            if topic_check == new_topic:
                autogen_worksheet = worksheet  # New worksheet assigned to this variable

        for expression in top_expressions:
            self.db_create_expression(autogen_worksheet, self.student, expression)

        # release the worksheet after giving it the new expressions
        autogen_worksheet.release()

        return


    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        worksheets = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)
        worksheets.filter(auto_student=self.student)
        expressionList = []




        context['complete'] = 0
        context['incomplete'] = 0
        context['ungraded']= 0
        context['expressionCount']= 0

        # TODO should this logic be in the worksheet model ? -Zeke
        for worksheet in worksheets:
            
            expression_filters = Q(worksheet=worksheet)
            if not worksheet.display_all_expressions:
                expression_filters &= (Q(student=self.student) | Q(student=None) | Q(all_do=True) | Q(worksheet=worksheet))
                expressions = Expression.objects.filter(expression_filters)

            last_submission = worksheet.last_submission(self.student)
            last_submission_status = last_submission.status if last_submission else "none"

            # Loop through and count status of worksheets/expressions
            if last_submission_status == "incomplete" or last_submission_status == "none":
                context['incomplete'] += 1
                for expression in expressions:
                    if expression.worksheet == worksheet:
                        expressionList.append(expression.expression)
            if last_submission_status == "complete":
                context['complete'] += 1
                for expression in expressions:
                    print('COMPLETE')
                    print(expression.expression)
                    if expression.worksheet == worksheet:
                        context['expressionCount'] += 1
            if last_submission_status == "ungraded":
                context['ungraded'] += 1
                for expression in expressions:
                    if expression.worksheet == worksheet:
                        expressionList.append(expression.expression)


            

            last_submission_id = last_submission.id if last_submission else 0
            status_colors = {
                "complete": "success",
                "incomplete": "danger",
                "ungraded": "warning",
                "pending": "light",
                "none": "info",
            }
            button_texts = {
                "complete": 'Review Worksheet',
                "incomplete": "Create Submission",
                "ungraded": "Edit Submission",
                "pending": "Complete Submission",
                "none": "Create Submission",
            }
            link_urls = {
                "complete": reverse("student:submission_list",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
                "incomplete": reverse("student:create_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
                "ungraded": reverse("student:update_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id, 'submission_id': last_submission_id}),
                "pending": reverse("student:create_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
                "none": reverse("student:create_submission",
                            kwargs={'course_id': self.course.id, 'worksheet_id': worksheet.id}),
            }

            worksheet.last_submission_status = last_submission_status
            worksheet.status_color = status_colors[last_submission_status]
            worksheet.button_text = button_texts[last_submission_status]
            worksheet.link_url = link_urls[last_submission_status]

        context['expressions'] = expressionList #list of expressions
        context['worksheets'] = worksheets

        return context


class SubmissionListView(StudentWorksheetViewMixin, ListView):
    template_name = 'ComSemApp/student/submission_list.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        return StudentSubmission.objects.filter(student=self.student, worksheet=self.worksheet)


class SubmissionUpdateCreateMixin(UpdateView):
    context_object_name = 'submission'
    template_name = "ComSemApp/student/create_submission.html"
    fields = []

    def get_context_data(self, **kwargs):
        context = super(SubmissionUpdateCreateMixin, self).get_context_data(**kwargs)
        context['previous_submissions'] = StudentSubmission.objects.filter(worksheet=self.worksheet, student=self.student).exclude(status__in=['pending', 'ungraded'])
        return context

    def get_success_url(self):
        return reverse("student:course", kwargs={'course_id': self.course.id })


class SubmissionCreateView(StudentWorksheetViewMixin, SubmissionUpdateCreateMixin):

    def get(self, request, *args, **kwargs):
        # student can't create a submission if there is an updatable one.
        if StudentSubmission.objects.filter(student=self.student, worksheet=self.worksheet, status__in=['ungraded', 'complete']).exists():
            messages.error(self.request, "You may not create a submission for this worksheet.")
            return HttpResponseRedirect(reverse("student:course", kwargs={'course_id': self.course.id }))
        return super().get(request, *args, **kwargs)

    def get_object(self):
        submission, created = StudentSubmission.objects.get_or_create_pending(self.student, self.worksheet)
        return submission

    def form_valid(self, form):
        self.object.status = 'ungraded'
        self.object.save()
        messages.success(self.request, "Submission successful")
        return super(SubmissionCreateView, self).form_valid(form)


class SubmissionUpdateView(StudentSubmissionViewMixin, SubmissionUpdateCreateMixin):
    # update view that doesn't actually change the object. only used for success_url

    def get_object(self):
        return get_object_or_404(StudentSubmission, id=self.submission.id, status="ungraded")

    def form_valid(self, form):
        messages.success(self.request, "Submission updated")
        return super(SubmissionUpdateView, self).form_valid(form)


class ExpressionListView(StudentSubmissionViewMixin, ListView):
    context_object_name = 'expressions'
    template_name = "ComSemApp/student/expression_list.html"

    def get_queryset(self):
        expression_filters = Q(worksheet=self.worksheet)
        if not self.worksheet.display_all_expressions:
            expression_filters &= (Q(student=self.student) | Q(student=None) | Q(all_do=True))
        expressions = Expression.objects.filter(expression_filters)
        for expression in expressions:
            attempt = None
            attempts = StudentAttempt.objects.filter(student_submission=self.submission, expression=expression)
            if attempts:
                attempt = attempts.first()
            expression.attempt = attempt
        return expressions


class AttemptCreateView(StudentSubmissionViewMixin, CreateView):
    model = StudentAttempt
    template_name = "ComSemApp/student/attempt_form.html"
    fields = ["reformulation_text", "audio"]

    def get_context_data(self, **kwargs):
        context = super(AttemptCreateView, self).get_context_data(**kwargs)
        # TODO - expression mixin rather than grabbing expression twice ?
        expression_id = self.kwargs.get('expression_id')
        expression = get_object_or_404(Expression, id=expression_id, worksheet=self.worksheet)
        context['expression'] = expression
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        expression_id = self.kwargs.get('expression_id')
        expression = get_object_or_404(Expression, id=expression_id, worksheet=self.worksheet)

        attempt = form.save(commit=False)
        attempt.student_submission = self.submission
        attempt.expression = expression
        attempt.save()
        return JsonResponse({}, status=200)


class AttemptUpdateView(StudentSubmissionViewMixin, UpdateView):
    context_object_name = 'attempt'
    template_name = "ComSemApp/student/attempt_form.html"
    fields = ["reformulation_text", "audio"]

    def get_context_data(self, **kwargs):
        context = super(AttemptUpdateView, self).get_context_data(**kwargs)
        context['expression'] = self.object.expression
        return context

    def get_object(self, **kwargs):
        attempt_id = self.kwargs.get('attempt_id')
        return get_object_or_404(StudentAttempt, student_submission=self.submission, id=attempt_id)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        attempt = form.save()
        if 'delete_audio' in form.data:
            attempt.audio = None
            attempt.save()
        return JsonResponse({}, status=200)
