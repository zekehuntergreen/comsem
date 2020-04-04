import json
import os

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

    def get_object(self):
        return self.course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        worksheets = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)

        # TODO should this logic be in the worksheet model ?
        for worksheet in worksheets: 
            complete_submission = worksheet.complete_submission(self.student) # vhl checks for complete submissions.
            complete_submission_status = 'complete' if complete_submission else "none"
        
            last_submission = worksheet.last_submission(self.student)
            last_submission_status = last_submission.status if last_submission else "none"
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
            
            
            # vhl checks for edge case where last submission is the not the complete attempt
            if complete_submission_status == 'complete': 
                last_submission_status = 'complete' 
            
            worksheet.last_submission_status = last_submission_status
            worksheet.status_color = status_colors[last_submission_status]
            worksheet.button_text = button_texts[last_submission_status]
            worksheet.link_url = link_urls[last_submission_status]
            
            
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
            messages.error(self.request, "You may not create a submission for this worksheet!!!.")
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


class ReviewsheetGeneratorView(StudentCourseViewMixin, DetailView):
    context_object_name = 'generate_reviewsheet'
    template_name = "ComSemApp/student/generate_reviewsheet.html"

    def get_object(self):
        return self.course

    def get_attempts(self, expression):

        submissions = StudentSubmission.objects.filter(student=self.student, worksheet=expression.worksheet)

        attempts = []
        for submission in submissions:
            try:
                sattempt = StudentAttempt.objects.get(student_submission=submission, expression=expression)
                attempts.append(sattempt)
            except:
                pass

        return attempts

    def get_expressions(self, worksheet, reactions):
        """ Get a list of expressions in a given worksheet
        
        Arguments:
            worksheet {Worksheet} -- a Worksheet object
        
        Returns:
            list -- a list of expressions contained in worksheet
        """
        import statistics
        if len(reactions) > 1:
            course_avg = statistics.mean(reactions) 
            course_std = statistics.stdev(reactions)
        else:
            course_avg = 0
            course_std = 1

        expression_filters = Q(worksheet=worksheet)
        if not worksheet.display_all_expressions:
            expression_filters &= (Q(student=self.student) | Q(student=None) | Q(all_do=True))

        expression_qset = Expression.objects.filter(expression_filters)

        for e in expression_qset:
            e.last_submission = StudentSubmission.objects.filter(student=self.student, worksheet=e.worksheet).latest('date').date.date()
            
            e.attempts = self.get_attempts(e)
            e.has_audio = False
            
            for a in e.attempts:
                if a.audio:
                    e.has_audio = True
            
            # AF - gets the number of attempts it took for the student to get the expression correct
            attempt_factor = len([x for x in e.attempts if not x.correct]) + 1
            
            # AF - gets the reviews
            past_correct_review = ReviewAttempt.objects.filter(expression=e.id, correct=True)
            past_incorrect_count = len(ReviewAttempt.objects.filter(expression=e.id, correct=False))
            
            # AF - get the number of days since reviewed or submitted an attempt
            if past_correct_review:
                time_since_view = (datetime.date.today() - past_correct_review.latest("date").date.date()).days
                expression_z = (statistics.mean([x.response_time for x in past_correct_review]) - course_avg)/course_std
            else:
                time_since_view = (datetime.date.today() - e.last_submission).days
                expression_z = 0

            # AF - placeholder algorithm: 1/(number of initial attempts + days since last seen  + 
            #      expression reaction time vs course reaction time z score + number of incorrect review attempts - number of correct review attempts)
            e.practice_score = int(100/(max(0, attempt_factor + time_since_view + expression_z + past_incorrect_count - len(past_correct_review)) + 1))

            if e.practice_score <= 33:
                e.bar_style = "bg-danger"
                e.border_style = "border-danger"
            elif e.practice_score <= 66:
                e.bar_style = "bg-warning"
                e.border_style = "border-warning"
            else:
                e.bar_style = "bg-primary"
                e.border_style = "border-success"
        
        return expression_qset

    def get_context_data(self, **kwargs):
        """Get worksheet data for a student in a given course
        
        Returns:
            dict -- context for creating generate_reviewsheet.html
        """
        context = super(ReviewsheetGeneratorView, self).get_context_data(**kwargs)
        worksheets = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)
        course_response_times = [x.response_time for x in ReviewAttempt.objects.filter(student=self.student, course=self.course, correct=True)]

        # TODO should this logic be in the worksheet model ?
        for worksheet in worksheets:
            last_submission = worksheet.last_submission(self.student)
            complete_submission = worksheet.complete_submission(self.student) # vhl checks for complete worksheets
            complete_submission_status = "complete" if complete_submission else "none"
    
            worksheet.last_submission_status = last_submission.status if last_submission else "none"
            if complete_submission_status == 'complete': # vhl if there is a complete worksheet
                worksheet.last_submission_status = 'complete'
            if worksheet.last_submission_status == 'complete':
                worksheet.expression_list = self.get_expressions(worksheet, course_response_times)

        # Only allow students to review completed worksheets (must have an answer)        
        context['worksheets'] =  [x for x in worksheets if x.last_submission_status == 'complete']


        return context

class ReviewsheetView(StudentCourseViewMixin, DetailView):
    # SHOULD THIS BE INHERETING ^^? 
    # Only using it since I want to keep non-central page elements the same (sidebar/header/footer)
    # Also I don't really know how to use Mixins properly -  AF

    context_object_name = 'reviewsheet'
    template_name = "ComSemApp/student/reviewsheet.html"

    def get_object(self):
        return self.course

    def get_attempts(self, expression):
        submissions = StudentSubmission.objects.filter(student=self.student, worksheet=expression.worksheet)

        attempts = []
        for submission in submissions:
            try:
                sattempt = StudentAttempt.objects.get(student_submission=submission, expression=expression)
                attempts.append(sattempt)
            except:
                pass

        return attempts

    def get_context_data(self, **kwargs):
        """Get worksheet data for a student in a given course
        
        Returns:
            dict -- context for creating generate_reviewsheet.html
        """
        
        context = super(ReviewsheetView, self).get_context_data(**kwargs)
        
        expression_ids = dict(self.request.GET)['choice']
        use_audio = dict(self.request.GET)['audio-choice'][0] == '1'
        print("AUDIO - ", use_audio)
        raw_expressions = []
        for expression_id in expression_ids:
            expression_object = get_object_or_404(Expression, pk=expression_id)
            expression_object.last_submission = StudentSubmission.objects.filter(student=self.student, worksheet=expression_object.worksheet).latest('date').date.date()
            expression_object.attempts = self.get_attempts(expression_object)
            raw_expressions.append(expression_object)
        
        review_data, audio_paths = self.make_review_questions(raw_expressions, use_audio) # vhl added use_audio bookmark2
        context['review_data'] = json.dumps(review_data)
        context['audio_paths'] = audio_paths
        context['student_id'] = self.student.id

        return context

    def make_review_questions(self, raw_expressions, use_audio):
        """ AF - Get expression data: expression ID, original expression, randomly selected term and answer 
        
        Arguments:
            raw_expressions {[list]} -- [A list of ]
            use_audio True if user wants audio False otherwise
        
        Returns:
            [type] -- [description]
        """
        import random
        
        reviewdata = []
        audio_paths = []
        
        
        for e in raw_expressions: 
            
            
            a_correct = [] # vhl list of correct expressions
            a_incorrect = [] # vhl list of incorrect expressions
            
                      
            a_incorrect.append(e) # vhl adds original expression to incorrect
    
            for attempt in e.attempts: # vhl goes through all attempts
                if use_audio and (attempt.audioCorrect is not None): # vhl check if attempt has audio and if user wants it
                    if attempt.audioCorrect: # vhl is audio correct
                        a_correct.append(attempt)
                    else: # vhl audio incorrect
                        a_incorrect.append(attempt)                                                                        
                else: # vhl if user does not want audio or attempt lacks audio
                    if attempt.correct is not None: # vhl prevents ungraded answers from getting on the review sheet
                        if attempt.correct: # vhl text attempt is correct
                            a_correct.append(attempt)
                        else: # vhl text attempt is incorrect
                            a_incorrect.append(attempt)
                
            if len(a_correct) == 0:  # vhl if there is somehow no correct ansswer
                selected = (a_incorrect[0], 'wrong')
            elif len(a_incorrect) == 0: # vhl if there is no incorrect answer
                selected = (a_correct[0], 'right')
            else: 
                if len(a_correct) == 1: # vhl if there is only 1 correct answer
                    correct_item = a_correct[0]
                else:
                    print(len(a_correct)) # vhl if there are multiple correct answers
                    correct_item = a_correct[random.randint(0, len(a_correct) - 1)]
                
                if len(a_incorrect) == 1: # vhl if there is only 1 incorrect answer
                    incorrect_item  = a_incorrect[0] 
                else: # vhl if there are multiple incorrect answers
                    incorrect_item = a_incorrect[random.randint(0, len(a_incorrect) - 1)]
                selected = [(correct_item, 'right'), (incorrect_item, 'wrong')][random.randint(0, 1)] # vhl randomly select a correct or incorrect question for the reviewsheet 
            
            
            expression_data = {'id': e.id, 'original': e.expression, 'answer': selected[1]}
            
            # Choose between audio and text

            if e == selected[0]: # vhl forces original expression to be text to prevent the instructors recording from being used.
                print("EXPRESSION")
                expression_data['term'] = selected[0].expression
                expression_data['type'] = 'TEXT'
             
                               
            elif selected[0].audio and use_audio: # vhl made it so audio only shows up when users request it
                # vhl case for if selected attempt has audio and user is looking for audio problems          
                print("AUDIO")
                expression_data['term'] = selected[0].reformulation_text
                a_id = "%d_audio" % e.id
                expression_data['audio_id'] = a_id
                audio_paths.append((a_id, selected[0].audio))
                expression_data['type'] = 'AUDIO'
            else: # vhl case for if a selected attempt has no audio or user does not want audio
                print("ATTEMPT")
                expression_data['term'] = selected[0].reformulation_text
                expression_data['type'] = 'TEXT'

            reviewdata.append(expression_data)
            
        return reviewdata, audio_paths

class ReviewsheetGetView(ReviewsheetView):
    def get(self, request, *args, **kwargs):
        # student can't create a submission if there is an updatable one.
        print(request.GET)
        if 'choice' in request.GET:
            return super().get(self, request, *args, **kwargs)
        else:
            messages.error(self.request, "You must select at least one expression to generate a worksheet")
            return HttpResponseRedirect(reverse("student:generate_reviewsheet", kwargs={'course_id': self.course.id }))

class ReviewAttemptCreateView(ReviewsheetView, CreateView):
    model = ReviewAttempt
    template_name = "ComSemApp/student/reviewsheet.html"
    fields = ["expression", "course", "student", "correct", "response_time"]

    def get_context_data(self, **kwargs):
        context = super(ReviewAttemptCreateView, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        form.save()
        return JsonResponse({}, status=200)
