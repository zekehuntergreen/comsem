import itertools
import json
from statistics import mean, stdev
import string
from typing import Any, Iterable
from datetime import datetime, timedelta
from random import choice, shuffle
from collections import Counter

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from ComSemApp.teacher import constants as teacher_constants

from ComSemApp.models import *
from ComSemApp.libs.mixins import RoleViewMixin, CourseViewMixin, WorksheetViewMixin, SubmissionViewMixin
from ComSemApp.utils import transcribe_and_get_length_audio_file

class StudentViewMixin(RoleViewMixin):

    role_class = Student

    def _set_role_obj(self):
        # role_obj self in RoleViewMixin
        self.student : Student = self.role_obj

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
        worksheets = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED).order_by('-date')

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
            messages.error(self.request, "You may not create a submission for this worksheet.")
            return HttpResponseRedirect(reverse("student:course", kwargs={'course_id': self.course.id }))
        return super().get(request, *args, **kwargs)

    def get_object(self):
        submission, _ = StudentSubmission.objects.get_or_create_pending(self.student, self.worksheet)
        return submission

    def form_valid(self, form):
        required_expressions = self.object.get_required_expressions()
        attempts = self.object.attempts.all()
        if attempts.count() < required_expressions.count():
            messages.warning(self.request, "Please create an attempt for each expression")
            return super().form_invalid(form)
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
        expressions = self.submission.get_required_expressions()
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
    
    def get_expressions(self, worksheet, reactions, weights):
        """ Get a list of expressions in a given worksheet
        --> 4.09.2020 Modified with new parameters
        
        Arguments:
            worksheet {Worksheet} -- a Worksheet object
        
        Returns:
            list -- a list of expressions contained in worksheet
        """
        if len(reactions) > 1:
            course_avg = mean(reactions) 
            course_std = stdev(reactions)
        else:
            course_avg = 0
            course_std = 1

        expression_filters = Q(worksheet=worksheet)
        if not worksheet.display_all_expressions:
            expression_filters &= (Q(student=self.student) | Q(student=None) | Q(all_do=True))

        expression_qset = Expression.objects.filter(expression_filters)
        exp_data = {"attempts":[], "days_since_review":[],  "rt":[], "pct_correct":[]}

        for e in expression_qset:
            e.last_submission = StudentSubmission.objects.filter(student=self.student, worksheet=e.worksheet).latest('date').date.date()
            
            e.attempts = self.get_attempts(e)
            e.has_audio = False
            
            for a in e.attempts:
                if a.audio:
                    e.has_audio = True
            
            # AF - gets the number of attempts it took for the student to get the expression correct
            attempt_factor = len([x for x in e.attempts if not x.text_correct]) + 1
            
            # AF - gets the reviews
            past_correct_review = ReviewAttempt.objects.filter(expression=e.id, correct=True)
            past_incorrect_count = len(ReviewAttempt.objects.filter(expression=e.id, correct=False))
            
            # AF - get the number of days since reviewed or submitted an attempt
            if past_correct_review:
                time_since_view = (datetime.date.today() - past_correct_review.latest("date").date.date()).days
                expression_z = (mean([x.response_time for x in past_correct_review]) - course_avg)/course_std
                avg_rt = mean([x.response_time for x in past_correct_review])
                
            else:
                time_since_view = (datetime.date.today() - e.last_submission).days
                expression_z = 0
                avg_rt = -1
                
            all_attempts = len(e.attempts) + len(past_correct_review) + past_incorrect_count
            pct_correct = (len(past_correct_review) + 1) / ( len(past_correct_review) + 1 + past_incorrect_count)
            
            e.raw_figs = {"attempts":all_attempts, "days_since_review":time_since_view,  "rt":avg_rt, "pct_correct":pct_correct}
            for f in e.raw_figs:
                exp_data[f].append(e.raw_figs[f])
        
        #mins = { x:min([y for y in exp_data[x] if y >= 0]) for x in exp_data}
        #ranges = { x:max([y for y in exp_data[x] if y >= 0 ]) - min([y for y in exp_data[x] if y >= 0]) for x in exp_data }
        # The previous two lines ran into an empty argument error wit min() and ranges would sometimes end up as 0
        # causing a divide by zero error later on. This was a quick fix near the end of the year so it migh tneed to be relooked at
        mins = {}
        ranges = {}
        
        for x in exp_data:
            check = False # vhl checks is there is a y > 0 otherwise you will get an error where the min function has not arguments
            for y in exp_data[x]:
                if y >= 0:
                    check = True
                    break
                                             
            if check: # if there is an appropriate min
                mins[x] = min([y for y in exp_data[x] if y >= 0]) 
                ranges[x] = max([y for y in exp_data[x] if y >= 0]) - min([y for y in exp_data[x] if y >= 0])
                if ranges[x] == 0:
                    ranges[x] = 1 # vhl I set this to 1 but only because it was dividing by 0
            else: # else set to default values to avoid divide by 0 errors
                mins[x] = 0
                ranges[x] = 1
                     
        
        for e in expression_qset:
            # e.norm_figs = {x:(e.raw_figs[x] - range_mins[x]['min']) / range_mins[x]['range'] if range_mins[x]['range'] > 0 else 0 for x in e.raw_figs }
            e.norm_figs = {}
            
            e.norm_figs['attempts'] = (0 if e.raw_figs['attempts'] == mins['attempts'] else (e.raw_figs['attempts'] - mins['attempts']) / ranges['attempts']) * weights['attempts']
            e.norm_figs['days_since_review'] = (1 if e.raw_figs['days_since_review'] == mins['days_since_review'] else 1 - (e.raw_figs['days_since_review'] - mins['days_since_review']) / ranges['days_since_review']) * weights['days_since_review']
            e.norm_figs['rt'] = (1 if e.raw_figs['rt'] == mins['rt'] else 1 - (e.raw_figs['rt'] - mins['rt']) / ranges['rt']) * weights['rt']
            e.norm_figs['pct_correct'] = (0 if e.raw_figs['pct_correct'] == mins['pct_correct'] else (e.raw_figs['pct_correct'] - mins['pct_correct']) / ranges['pct_correct']) * weights['pct_correct']
            e.practice_score = int(sum(e.norm_figs.values()) * 100)
            
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
        
        WEIGHTS = {"attempts":0.1, "days_since_review":0.2,  "rt":0.2, "pct_correct":0.5} #a static that we can change later if we want to add adjustable weights
        context = super(ReviewsheetGeneratorView, self).get_context_data(**kwargs)
        worksheets = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)
        course_response_times = [x.response_time for x in ReviewAttempt.objects.filter(
                    student=self.student, expression__worksheet__course=self.course, correct=True)]
        exp_data = {"attempts":[], "days_since_review":[],  "rt":[], "pct_correct":[]}
        
        # TODO should this logic be in the worksheet model ?
        for worksheet in worksheets:
            last_submission = worksheet.last_submission(self.student)
            complete_submission = worksheet.complete_submission(self.student) # vhl checks for complete worksheets
            complete_submission_status = "complete" if complete_submission else "none"
    
            worksheet.last_submission_status = last_submission.status if last_submission else "none"
            if complete_submission_status == 'complete': # vhl if there is a complete worksheet
                worksheet.last_submission_status = 'complete'
            if worksheet.last_submission_status == 'complete':
                worksheet.expression_list = self.get_expressions(worksheet, course_response_times, WEIGHTS)
                for e in worksheet.expression_list:
                    for f in exp_data:
                        exp_data[f].append(e.raw_figs[f])
            
        #mins = { x: min([y for y in exp_data[x] if y >= 0]) for x in exp_data}
        #ranges = { x:max([y for y in exp_data[x] if y >= 0]) - min([y for y in exp_data[x] if y >= 0]) for x in exp_data }
        # The previous two lines ran into an empty argument error wit min() and ranges would sometimes end up as 0
        # causing a divide by zero error later on. This was a quick fix near the end of the year so it migh tneed to be relooked at
        mins = {}
        ranges = {}
        
        for x in exp_data: 
            check = False # vhl checks is there is a y > 0 otherwise you will get an error on new worksheets where there is none
            for y in exp_data[x]:
                if y >= 0: # if there is a y > 0 then min will not have empty arguments
                    check = True
                    break
                                             
            if check: 
                mins[x] = min([y for y in exp_data[x] if y >= 0]) 
                ranges[x] = max([y for y in exp_data[x] if y >= 0]) - min([y for y in exp_data[x] if y >= 0])
                if ranges[x] == 0:
                    ranges[x] = 1 # there was a divide by 0 error
            else: # default values
                mins[x] = 0
                ranges[x] = 1
        
        
        completed = [x for x in worksheets if x.last_submission_status == 'complete']
        for w in completed:
            for e in w.expression_list:
                e.norm_figs = {}
                
                e.norm_figs['attempts'] = (0 if e.raw_figs['attempts'] == mins['attempts'] else (e.raw_figs['attempts'] - mins['attempts']) / ranges['attempts']) * WEIGHTS['attempts']
                e.norm_figs['days_since_review'] = (1 if e.raw_figs['days_since_review'] == mins['days_since_review'] else 1 - (e.raw_figs['days_since_review'] - mins['days_since_review']) / ranges['days_since_review']) * WEIGHTS['days_since_review']
                e.norm_figs['rt'] = (1 if e.raw_figs['rt'] == mins['rt'] else 1 - (e.raw_figs['rt'] - mins['rt']) / ranges['rt']) * WEIGHTS['rt']
                e.norm_figs['pct_correct'] = (0 if e.raw_figs['pct_correct'] == mins['pct_correct'] else (e.raw_figs['pct_correct'] - mins['pct_correct']) / ranges['pct_correct']) * WEIGHTS['pct_correct']
                e.practice_score = int(sum(e.norm_figs.values()) * 100)

        # Only allow students to review completed worksheets (must have an answer)        
        context['worksheets'] =  completed
        
        return context


class ReviewsheetView(StudentCourseViewMixin, DetailView):

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
        raw_expressions = []
        for expression_id in expression_ids:
            expression_object = get_object_or_404(Expression, pk=expression_id)
            expression_object.last_submission = StudentSubmission.objects.filter(student=self.student, worksheet=expression_object.worksheet).latest('date').date.date()
            expression_object.attempts = self.get_attempts(expression_object)
            raw_expressions.append(expression_object)
        
        review_data, audio_paths = self.make_review_questions(raw_expressions, use_audio) # vhl makes reviewsheet questions
        context['review_data'] = json.dumps(review_data)
        context['audio_paths'] = audio_paths
        context['student_id'] = self.student.id

        return context

    def make_review_questions(self, raw_expressions, use_audio):
        """ AF - Get expression data: expression ID, original expression, randomly selected term and answer 
        
        Arguments:
            raw_expressions {[list]} -- [A list of expressions]
            use_audio -- True if user wants audio False otherwise
        
        Returns:
            [type] -- [description]
        """
        import random

        review_data = []
        audio_paths = [] 


        for e in raw_expressions: 
            a_correct = [] # vhl list of correct expressions
            a_incorrect = [] # vhl list of incorrect expressions

            a_incorrect.append(e) # vhl adds original expression to incorrect
            for attempt in e.attempts: # vhl goes through all attempts
                if use_audio and (attempt.audio_correct is not None): # vhl check if attempt has audio and if user wants it
                    if attempt.audio_correct: # vhl is audio correct
                        a_correct.append(attempt)
                    else: # vhl audio incorrect
                        a_incorrect.append(attempt)
                else: # vhl if user does not want audio or attempt lacks audio
                    if attempt.text_correct is not None: # vhl prevents ungraded answers from getting on the review sheet
                        if attempt.text_correct: # vhl text attempt is correct
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
                    # vhl if there are multiple correct answers
                    correct_item = a_correct[random.randint(0, len(a_correct) - 1)]
                
                if len(a_incorrect) == 1: # vhl if there is only 1 incorrect answer
                    incorrect_item  = a_incorrect[0] 
                else: # vhl if there are multiple incorrect answers
                    incorrect_item = a_incorrect[random.randint(0, len(a_incorrect) - 1)]
                    
                selected = [(correct_item, 'right'), (incorrect_item, 'wrong')][random.randint(0, 1)] # vhl randomly select a correct or incorrect question for the reviewsheet 



            expression_data = {'id': e.id, 'original': e.expression, 'answer': selected[1]}

            # Choose between audio and text

            if e == selected[0]: # vhl forces original expression to be text to prevent the instructors recording from being used.
                expression_data['term'] = selected[0].expression
                expression_data['type'] = 'TEXT'

            elif selected[0].audio and use_audio and selected[0].audio_correct is not None: # vhl made it so audio only shows up when users request it and audio has been graded correctly
                # Last conditional is for audio expressions graded before audio_correct was in models.
                # vhl case for if selected attempt has audio and user is looking for audio problems          
                expression_data['term'] = selected[0].reformulation_text
                a_id = "%d_audio" % e.id
                expression_data['audio_id'] = a_id
                audio_paths.append((a_id, selected[0].audio))
                expression_data['type'] = 'AUDIO'
            else: 
                # vhl case for if a selected attempt has no audio or user does not want audio
                expression_data['term'] = selected[0].reformulation_text
                expression_data['type'] = 'TEXT'

            review_data.append(expression_data)

        return review_data, audio_paths


class ReviewsheetGetView(ReviewsheetView):
    def get(self, request, *args, **kwargs):
        # student can't create a submission if there is an updatable one.
        if 'choice' in request.GET:
            return super().get(self, request, *args, **kwargs)
        else:
            messages.error(self.request, "You must select at least one expression to generate a worksheet")
            return HttpResponseRedirect(reverse("student:generate_reviewsheet", kwargs={'course_id': self.course.id }))


class ReviewAttemptCreateView(ReviewsheetView, CreateView):
    model = ReviewAttempt
    template_name = "ComSemApp/student/reviewsheet.html"
    fields = ["expression", "student", "correct", "response_time"]

    def get_context_data(self, **kwargs):
        context = super(ReviewAttemptCreateView, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        form.save()
        return JsonResponse({}, status=200)

# ALL THESE CLASSES SHOULD IMPLEMENT DIFFERENT VIEWS LATER
# the foo() functions are just placeholders too keep the classes in here
class SpeakingPracticeInfoMixin(object):
    def get_expression_data(self, attempts : QuerySet[SpeakingPracticeAttempt]) -> dict[str, float | int]:
        """
        Gathers the relevant data for an expression given the queryset of attempts for that expression

        Arguments:
            attempts : QuerySet[SpeakingPracticeAttempt] -- The QuerySet of attempts for an expression

        Returns:
            data : dict[str : float | int] -- The aggregate data for the expression (correct_attempts, days_since_review, wpm, last_score)
        """
        # data is initialized with the worst possible values
        data : dict[str, float | int] = {'correct_attempts' : 0, 'days_since_review' : 999, 'wpm' : 0, 'last_score' : 0}
        correct_attempts : QuerySet[SpeakingPracticeAttempt]
        last_attempt : SpeakingPracticeAttempt
        curr_time : datetime 

        if(attempts.count() == 0):
            return data
        
        correct_attempts = attempts.filter(correct=100)
        data['correct_attempts'] = correct_attempts.count()
        data['wpm'] = mean([attempt.wpm for attempt in correct_attempts]) if data['correct_attempts'] > 0 else 0

        # Get the current date in UTC so python allows us to compare with the dates in the database
        curr_time = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        last_attempt = attempts.latest('session__date')
        data['days_since_review'] = (curr_time - last_attempt.session.date).days
        data['last_score'] = last_attempt.correct

        return data

class SpeakingPracticeView(StudentViewMixin, CourseViewMixin, TemplateView):
    """
      Serves the content of the speaking practice page which presents problems
      and recieves user input.
    """
    template_name : str = 'ComSemApp/student/assessment.html'

    def generate_problem_info(self, id : str) -> dict[str, str | int]:
        """
          Generates a speaking practice problem for an expression given the id of that expression

        Arguments:
          id : str -- The id of the expression

        Returns:
          problem_data : dict[str : str | int] -- The problem data for the given expression, contains:
            ['id'] : str -- the expression id
            ['formulation'] : str -- the expression formulation to be displayed
            ['syllables'] : int -- the number of syllables in the correct formulation
        """
        problem_data : dict[str : str | float] = {}
        valid_formulations : list[str] = []
        correct_formulations : list[str] = []
        expression_object : Expression = None
        attempts : QuerySet[StudentAttempt] = StudentAttempt.objects.filter(student_submission__student=self.student, expression=id)

        try:
            expression_object = Expression.objects.get(pk=id)
        except(Expression.DoesNotExist):
            return None

        if not attempts:
            return None

        valid_formulations = [attempt.reformulation_text for attempt in attempts if attempt.reformulation_text and attempt.text_correct == False]
        valid_formulations.append(expression_object.expression)

        correct_formulations = [attempt.reformulation_text for attempt in attempts if attempt.reformulation_text and attempt.text_correct == True]
        
        problem_data['id'] = id
        problem_data['formulation'] = choice(valid_formulations)
        # this is an extremely primitive way to find syllable count, but is fine for a demo/beta
        problem_data['syllables'] = round(max(len(formulation) for formulation in correct_formulations)) / 2

        return problem_data

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
          Gets the data necessary to create speaking practice problems 
          from expressions given in a GET request

        Returns:
          context -- context data used by assessment.html
        """
        context : dict[str, Any] = super(SpeakingPracticeView, self).get_context_data(**kwargs)
        context['problems'] : list[dict[str, str | float]] = {}
        context['student'] : int = self.student.pk

        session : SpeakingPracticeSession = SpeakingPracticeSession.objects.filter(student=self.student).latest('date')
        if session is None or session.attempts.count() != 0:
            session = SpeakingPracticeSession(student=self.student)
            session.save()
        context['session'] = session.id

        expression_ids : list[str] = dict(self.request.GET)['choice']
        # This list comprehension grabs all the data necessary for problems and filters out invalid expressions
        context['problems'] = [problem_data for expression_id in expression_ids if (problem_data := self.generate_problem_info(expression_id)) is not None]
        shuffle(context['problems'])

        return context

class SpeakingPracticeGeneratorView(StudentCourseViewMixin, DetailView, SpeakingPracticeInfoMixin):
    """
      Serves the expression selection page wherein students are presented with
      a list of expressions grouped by worksheet along with their familiarity scores
      to select from for a practice session
    """
    # These class variables are a necessary part of the Django DetailView class
    context_object_name : str = 'speaking_practice_generator'
    template_name: str = 'ComSemApp/student/assessment_generator.html'
    
    def get_object(self):
        return self.course
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """
            Implements Django's DetailView.get_context_data to provide data for the template
        
            Returns:
                context -- context data used by assessment_generator.html
        """
        context : dict[str, Any] = super(SpeakingPracticeGeneratorView, self).get_context_data(**kwargs)
        worksheets : QuerySet[Worksheet] = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)
        practice_attempts : QuerySet[SpeakingPracticeAttempt] = SpeakingPracticeAttempt.objects.filter(session__student=self.student, expression__worksheet__course=self.course)
        completed : list[Worksheet] = []
        # every completed expression will have an entry in exp_data
        # each entry will have the following data: 'correct_attempts', 'days_since_review', 'wpm', 'last_score'
        exp_data : dict[Expression, dict[str, float | int]] = {}
        WEIGHTS : dict[str,float] = {'correct_attempts': 0.15, 'days_since_review' : 0.1,  'wpm' : 0.25, 'last_score' : 0.5}
        DATA_KEYS : list[str] = ['correct_attempts', 'days_since_review', 'wpm', 'last_score']

        completed = [i for i in worksheets if i.complete_submission(self.student)]
        for worksheet in completed:
            worksheet.expression_list : QuerySet[Expression] = worksheet.expressions.all().filter(Q(student=self.student) | Q(student=None) | Q(all_do=True))
            for expression in worksheet.expression_list:
                exp_data[expression] = self.get_expression_data(practice_attempts.filter(expression=expression))
    
        mins = { key : min([y[key] for y in exp_data.values()]) for key in DATA_KEYS }
        maxes = { key: max([y[key] for y in exp_data.values()]) for key in DATA_KEYS }
        ranges = { key : maxes[key] - mins[key] if maxes[key] > mins[key] else 1 for key in DATA_KEYS }

        for worksheet in completed:
            for expression in worksheet.expression_list:
                expression.norm_figs : dict[str, int | float] = {}
                
                # These weights are based on the formula: attempt - min / range
                # the days_since_review score is subtracted from one since less days since review is higher familiarity
                expression.norm_figs['correct_attempts'] = max(1, exp_data[expression]['correct_attempts'] - mins['correct_attempts']) / ranges['correct_attempts']
                expression.norm_figs['days_since_review'] = 1 - (max(0, exp_data[expression]['days_since_review'] - mins['days_since_review']) / ranges['days_since_review'])
                expression.norm_figs['wpm'] = max(1, exp_data[expression]['wpm'] - mins['wpm']) / ranges['wpm']
                expression.norm_figs['last_score'] = max(1, exp_data[expression]['last_score'] - mins['last_score']) / ranges['last_score']
                expression.familiarity : int = round(sum([float(expression.norm_figs[key]) * WEIGHTS[key] for key in DATA_KEYS]) * 100)

                # we need to set the style of each expression's score bar
                (expression.bar_style, expression.border_style) = \
                    ('bg-danger','border-danger') if expression.familiarity <= 33 \
                    else ('bg-warning','border-warning') if expression.familiarity <= 66 \
                    else ('bg-primary','border-success')

        # Only allow students to review completed worksheets (must have an answer)        
        context['worksheets'] =  completed
        
        return context

class SpeakingPracticeResultsView(StudentViewMixin, CourseViewMixin, DetailView, SpeakingPracticeInfoMixin):
    """
      Serves the content of the speaking practice results page presented after a
      session of practice.
    """
    template_name: str = 'ComSemApp/student/assessment_results.html'

    def get_object(self):
        """
            implements Django DetailView function
        """
        return self.course

    def get_context_data(self, **kwargs) -> dict[str, dict[str, str | int | float]]:
        """
            implements Django's DetailView get_context_data function 
            Returns:
                context -- context data used by assessment_results.html
        """
        context : dict[str, Any] = super(SpeakingPracticeResultsView, self).get_context_data(**kwargs)
        context['attempts'] : list[dict[str, str | float]] = {}
        try:
            attempt_ids : list[str] = dict(self.request.GET)['attempt_ids']
        except:
            return context
        attempts : QuerySet[SpeakingPracticeAttempt] = SpeakingPracticeAttempt.objects.filter(session__student=self.student, pk__in=attempt_ids)
        expressions : set[Expression] = set([attempt.expression for attempt in attempts])
        familiarity_scores : dict[int, int] = {}

        # In order to generate familiarity scores, we must get some data for all expressions.
        worksheets : QuerySet[Worksheet] = self.course.worksheets.filter(status=teacher_constants.WORKSHEET_STATUS_RELEASED)
        practice_attempts : QuerySet[SpeakingPracticeAttempt] = SpeakingPracticeAttempt.objects.filter(session__student=self.student, expression__worksheet__course=self.course)
        completed : list[Worksheet] = []
        exp_data : dict[Expression, dict[str, float | int]] = {}
        WEIGHTS : dict[str,float] = {'correct_attempts': 0.15, 'days_since_review' : 0.1,  'wpm' : 0.25, 'last_score' : 0.5}
        DATA_KEYS : list[str] = ['correct_attempts', 'days_since_review', 'wpm', 'last_score']

        completed = [i for i in worksheets if i.complete_submission(self.student)]
        for worksheet in completed:
            expression_list : QuerySet[Expression] = worksheet.expressions.all().filter(Q(student=self.student) | Q(student=None) | Q(all_do=True))
            for expression in expression_list:
                exp_data[expression] = self.get_expression_data(practice_attempts.filter(expression=expression))
        
        mins = { key : min([y[key] for y in exp_data.values()]) for key in DATA_KEYS }
        maxes = { key: max([y[key] for y in exp_data.values()]) for key in DATA_KEYS }
        ranges = { key : maxes[key] - mins[key] if maxes[key] > mins[key] else 1 for key in DATA_KEYS }

        for expression in expressions:
            normalized_data : dict[str, int | float] = {}
            normalized_data['correct_attempts'] = max(0, exp_data[expression]['correct_attempts'] - mins['correct_attempts']) / ranges['correct_attempts']
            normalized_data['days_since_review'] = 1 - (max(0, exp_data[expression]['days_since_review'] - mins['days_since_review']) / ranges['days_since_review'])
            normalized_data['wpm'] = max(0, exp_data[expression]['wpm'] - mins['wpm']) / ranges['wpm']
            normalized_data['last_score'] = max(0, exp_data[expression]['last_score'] - mins['last_score']) / ranges['last_score']
            familiarity_scores[expression.pk] = round(sum([float(normalized_data[key]) * WEIGHTS[key] for key in DATA_KEYS]) * 100)

        context['attempts'] = [
            {
            'id' : attempt.pk,
            'transcription' : attempt.transcription,
            'audio_path' : attempt.audio.url,
            'score' : attempt.correct,
            'expression_id' : expression.pk,
            'incorrect_expression': attempt.expression.expression,
            'correct_formulation' : attempt.expression.reformulation_text,
            'familiarity' : familiarity_scores[attempt.expression.pk]
            } for attempt in attempts]

        return context

class SpeakingPracticeInstructionsView(StudentViewMixin, CourseViewMixin, TemplateView):
    """
      Serves the instructions page for the speaking practice tool.
    """
    template_name: str = 'ComSemApp/student/assessment_instructions.html'

    def foo():
        pass

class SpeakingPracticeAttemptCreateView(StudentCourseViewMixin, CreateView):
    """
        Used to process form data served from the SpeakingPracticeView on the frontend.
        Implements the standard Django CreateView
    """
    model = SpeakingPracticeAttempt
    fields = ["expression", "session", "audio"]

    def score_generator(self, transcription : str, expression : Expression) -> Iterable[tuple[float, StudentAttempt | None]]:
        """
            Generator function which returns an Iterable over score tuples, which include the 
            associated StudentAttempt if applicable

            Arguments:
                transcription : str -- The transcription to grade against all correct worksheet attempts
                expression : Expression -- The Expression object associated with the speaking practice attempt

            Remarks:
                As a generator function, this follows the python generator model with the use of the
                yield keyword. When .next() is called on the returned iterable, the function is run
                until a yield statement is met, and the yielded value is returned as the result of the
                .next() call. Every subsequent time .next() is called, execution resumes from the
                previous yield statement.
                It is strongly recommended to read Python's official documentation of generator.
        """
        MAX_SCORE : float = 100
        score : float
        correct_attempts : QuerySet[StudentAttempt] = StudentAttempt.objects.filter(expression=expression, text_correct=True)

        # All strings are made lowercase and have their punctuation removed for comparison
        transcription = transcription.lower().translate(str.maketrans('', '', string.punctuation))
        score = self.grade_against_correct(transcription, expression.reformulation_text.lower().translate(str.maketrans('', '', string.punctuation)))
        yield (score, None)
        for attempt in correct_attempts:
            if score == MAX_SCORE:
                return
            score = self.grade_against_correct(transcription, attempt.reformulation_text.lower().translate(str.maketrans('', '', string.punctuation)))
            yield (score, attempt)
        return

    def grade_against_correct(self,transcription : string, correct_formulation : string):
        # TODO: Implement
        return 100

    def form_invalid(self, form):
        """
            Defines the behavior for an invalid form submission.
            Reports whatever errors are found back to the frontend.
        """
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        """
            Defines the behavior for a valid form submission.
            Processes audio data from the form, creates the SpeakingPracticeAttempt
            entry in the database and returns the transcription and score data back to the frontend
        """
        attempt : SpeakingPracticeAttempt = form.save(commit=False)
        transcription : str
        length : int
        score : tuple[float, StudentAttempt | None]

        if attempt.session.student != self.student:
            return HttpResponse(f"Student does not own session {attempt.session}", status=403)

        transcription, length = transcribe_and_get_length_audio_file(attempt.audio)
        # The Counter call gets the number of words, the division on the bottom get the length in minutes
        attempt.wpm = Counter(transcription.split()).total() / (length / 60000)
        score = max(self.score_generator(transcription,attempt.expression), key=lambda score : score[0])
        attempt.correct = score[0]
        # TODO: ADD ASSOCIATED STUDENTATTEMPT ONCE MODEL IS UPDATED
        attempt.transcription = transcription

        attempt.save()
        return JsonResponse({'id' : attempt.id}, status=201)

class SpeakingPracticeReviewDetailView(StudentViewMixin, CourseViewMixin, DetailView, SpeakingPracticeInfoMixin):
    """
      Serves the content of the speaking practice results page presented after a
      session of practice.
    """
    template_name: str = 'ComSemApp/student/speaking_practice_review.html'

    def get_object(self):
        """
            implements Django DetailView function
        """
        return self.course

    def get_context_data(self, **kwargs) -> dict[str, dict[str, str | int | float]]:
        """
            implements Django's DetailView get_context_data function 
            Returns:
                context -- context data used by assessment_results.html
        """
        context : dict[str, Any] = super(SpeakingPracticeReviewDetailView, self).get_context_data(**kwargs)
        return context

class SpeakingPracticeReviewSessionListView(StudentViewMixin, CourseViewMixin, SpeakingPracticeInfoMixin, ListView):
    '''
        Serves the context object of session information for the Speaking Practice Sessions List
    '''
    context_object_name = 'sessions'
    template_name = "ComSemApp/student/speaking_practice_sessions_list.html"

    def get_queryset(self):
        # grabs the sessions for the student and the course
        sessions : QuerySet[SpeakingPracticeSession] = SpeakingPracticeSession.objects.filter(student=self.student, attempts__expression__worksheet__course= self.course).distinct().order_by('-date')
        
        # formats the context data with correct info
        sessions_data = [
            {
                'id':session.id,
                'date':session.date,
                'avg_score': session.average_correctness()
            } for session in sessions]
        return sessions_data

class SpeakingPracticeReviewRequestListView(StudentViewMixin, CourseViewMixin, SpeakingPracticeInfoMixin, ListView):
    '''
        Serves the context object of review request information for the Speaking Practice Review Request List on the student side
    '''
    context_object_name = 'requests'
    template_name = "ComSemApp/student/speaking_practice_requests_list.html"

    def get_queryset(self):
        # grabs the requests for the student and course
        requests : QuerySet[SpeakingPracticeAttemptReviewRequest] = SpeakingPracticeAttemptReviewRequest.objects.filter(attempt__expression__worksheet__course=self.course, attempt__session__student=self.student).order_by('-date')
        
        # formats the context data with the correct info
        request_data = [
            {
                'id':request.pk,
                'expression':request.attempt.transcription,
                'date':request.date,
                'session': request.attempt.session.id,
                'reviewed': request.is_reviewed(),

            } for request in requests]
    
        return request_data