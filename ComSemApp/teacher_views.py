from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.http import JsonResponse
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.core.serializers import serialize
from django.contrib import messages
from django.conf import settings


import json, math, datetime, os
from .models import *


# DECORATORS
def is_teacher(user):
    return Teacher.objects.filter(user=user).exists()

def teaches_course(func):
    def wrapper(request, *args, **kwargs):
        valid = Course.objects.filter(teachers=request.user.teacher, id=args[0]).exists()
        if not valid:
            messages.error(request, 'Invalid course ID.')
            return redirect("/teacher/")
        return func(request, *args, **kwargs)
    return wrapper


def teaches_course_ajax(func):
    def wrapper(request, *args, **kwargs):
        course_id = request.POST.get('course_id', None)
        worksheet_id = request.POST.get('worksheet_id', None)

        # might need to seach for courseid from worksheetid
        if worksheet_id and int(worksheet_id) > 0:
            course_id = get_object_or_404(Worksheet, id=worksheet_id).course.id

        valid = Course.objects.filter(teachers=request.user.teacher, id=course_id).exists()
        if not valid:
            response = JsonResponse({"error": 'Invalid course ID.'})
            response.status_code = 403
            return response
        return func(request, *args, **kwargs)
    return wrapper




# VIEWS
@login_required
@user_passes_test(is_teacher)
def teacher(request):
    courses = Course.objects.filter(teachers=request.user.teacher)
    show_active_button = any(course.is_active() for course in courses) # we'll show the course status button group only if there is a mix of active, inactive courses
    template = loader.get_template('ComSemApp/teacher/my_courses.html')
    return HttpResponse(template.render({'courses': courses, 'show_active_button': show_active_button, 'teacher_view': True}, request))


@login_required
@user_passes_test(is_teacher)
@teaches_course_ajax
def course_students(request):
    course_id = request.POST.get('course_id', None)
    course = Course.objects.get(id=course_id)

    template = loader.get_template('ComSemApp/teacher/course_students.html')
    context = {
        'course': course,
    }
    return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_teacher)
@teaches_course
def course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    worksheets = Worksheet.objects.filter(course=course)

    template = loader.get_template('ComSemApp/teacher/course.html')
    context = {
        'course': course,
        'worksheets': worksheets,
    }
    return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_teacher)
@teaches_course_ajax
def delete_worksheet(request):
    worksheet_id = request.POST.get('worksheet_id', None)
    worksheet = get_object_or_404(Worksheet, id=worksheet_id)
    worksheet.delete()
    return HttpResponse(status=204)



@login_required
@user_passes_test(is_teacher)
@teaches_course_ajax
def release_worksheet(request):
    worksheet_id = request.POST.get('worksheet_id', None)
    worksheet = get_object_or_404(Worksheet, id=worksheet_id)
    Worksheet.objects.filter(id=worksheet.id).update(released=True)
    return HttpResponse(status=204)


@login_required
@user_passes_test(is_teacher)
@teaches_course
def worksheet(request, course_id, worksheet_id):
    # EITHER the worksheet is unreleased and we are editing it OR it is released and we are reviewing submissions

    course = get_object_or_404(Course, id=course_id)

    context = {
        'course': course,
    }

    # if this is NOT a new worksheet
    template = loader.get_template('ComSemApp/teacher/edit_worksheet.html')

    if worksheet_id != '0':

        worksheet = get_object_or_404(Worksheet, id=worksheet_id)
        context['worksheet'] = worksheet

        # get related expression information and serialize it
        expression_queryset = Expression.objects.filter(worksheet=worksheet).prefetch_related('student')


        if not course.id != course_id:
            return HttpResponse("Invalid course ID")

        if worksheet.released == True:
            context['expressions'] = expression_queryset
            context['submissions'] = StudentSubmission.objects.filter(worksheet=worksheet)
            template = loader.get_template('ComSemApp/teacher/view_worksheet.html')

        else:
            expressions_json = jsonify_expressions(expression_queryset)
            context['expressions'] = expressions_json

            template = loader.get_template('ComSemApp/teacher/edit_worksheet.html')


    return HttpResponse(template.render(context, request))



@login_required
@user_passes_test(is_teacher)
@teaches_course_ajax
def save_worksheet(request):

    # get form data
    course_id = request.POST.get('course_id', None)
    worksheet_id = request.POST.get('worksheet_id', None)
    topic = request.POST.get('topic', None)
    display_original = request.POST.get('display_original', None) == 'true'
    display_reformulation_text = request.POST.get('display_reformulation_text', None) == 'true'
    display_reformulation_audio = request.POST.get('display_reformulation_audio', None) == 'true'
    display_all_expressions = request.POST.get('display_all_expressions', None) == 'true'
    expressions = json.loads(request.POST.get('expressions', None))

    course = Course.objects.get(id=course_id)

    # topic could be in db already - get or create
    topic_obj, created = Topic.objects.get_or_create(topic=topic)

    values = {
        'course': course,
        'topic': topic_obj,
        'released': False,
        'display_original': display_original,
        'display_reformulation_text': display_reformulation_text,
        'display_reformulation_audio': display_reformulation_audio,
        'display_all_expressions': display_all_expressions,
    }

    worksheet = {}
    if worksheet_id > '0':
        Worksheet.objects.filter(id=worksheet_id).update(**values)
        worksheet = Worksheet.objects.get(id=worksheet_id)
    else:
        worksheet = Worksheet.objects.create(**values)

    print (worksheet, type(worksheet))

    # deal with expressions
    for i in range(len(expressions)):
        expression = expressions[i]
        # print (expression, type(expression))

        student = None
        if expression['student_id']:
            student = get_object_or_404(Student,id=expression['student_id']) # if they passed a student id, then it must be valid

            ## is student in course???


        # deal with audio reformulation - has the audio been uploaded?
        ra_key = 'audio_ref_' + str(i);
        # either there is an old audio reformulation already saved, or we are saving a new one.
        uploading_ra = request.FILES.get(ra_key, None)
        ra_is_there = True if expression['reformulation_audio'] else True if uploading_ra else False
        print(expression['reformulation_audio'])
        print(uploading_ra)
        print (ra_is_there)
        values = {
            'worksheet': worksheet,
            'expression': expression['expression'],
            'student': student,
            'context_vocabulary': expression['context_vocabulary'],
            'pronunciation': expression['pronunciation'],
            'reformulation_text': expression['reformulation_text'],
            'reformulation_audio': ra_is_there,
        }


        expression_id = expression['id']
        expression_obj = {}

        # new expression
        if expression_id == '0':
            expression_obj = Expression.objects.create(**values)
            expression_id = expression_obj.id

        # edit expression
        else:
            if 'to_delete' in expression:
                Expression.objects.get(id=expression_id).delete()
            else:
                Expression.objects.filter(id=expression_id).update(**values)

        # save the audio reformulation
        if uploading_ra:
            handle_uploaded_file(uploading_ra, "ExpressionReformulations", int(expression_id))


    return HttpResponse(status=204)


@login_required
@user_passes_test(is_teacher)
@teaches_course
def submission(request, course_id, worksheet_id, submission_id):

    course = get_object_or_404(Course, id=course_id)
    worksheet = get_object_or_404(Worksheet, id=worksheet_id)
    submission = get_object_or_404(StudentSubmission, id=submission_id)

    # user completed assessment form
    if request.method == 'POST':
        attempts = submission.studentattempt_set.all()

        all_correct = True
        # status of each attempt
        for attempt in attempts:
            correct = request.POST.get(str(attempt.id), None) == '1'
            attempt.correct = correct
            attempt.save()

            if not correct:
                all_correct = False

        # handle status of the submission
        if all_correct:
            submission.status = 'complete'
        else:
            submission.status = 'incomplete'

        submission.save()

        messages.error(request, 'Assessment saved ', 'success')
        return redirect('teacher_worksheet', course_id, worksheet_id)

    # displaying submission
    else:


        context = {
            'course': course,
            'worksheet': worksheet,
            'submission': submission,
        }

        template = loader.get_template('ComSemApp/teacher/view_submission.html')
        return HttpResponse(template.render(context, request))


def jsonify_expressions(expression_queryset):
    expressions = list(expression_queryset.values())

    # need to get name of assigned student seperately
    for i in range(len(expressions)):
        student = expression_queryset[i].student
        expressions[i]['student_name'] = str(student) if student else None
        expressions[i]['reformulation_audio'] = False if expressions[i]['reformulation_audio'] == '0' else True

    return json.dumps(expressions)


def handle_uploaded_file(f, directory, e):
    id_floor = int(math.floor(e/1000))
    url = settings.EFS_DIR
    url += directory + '/' + str(id_floor)
    if not os.path.exists(url):
        os.makedirs(url)
    filename = e - (id_floor * 1000)
    url += '/' + str(filename) + ".mp3"
    with open(url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
