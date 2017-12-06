from django.shortcuts import render
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

import json, math, datetime, os
from .models import *

# TESTS
def is_teacher(user):
    return user.groups.filter(name='teacher').exists()

# is user a teacher in the course?
def teaches_course(teacher, course_id):
    return TeachingInstance.objects.filter(teacher=teacher, course_id=course_id).exists()


def index(request):
    return HttpResponse("<b>Communication Seminar</b> index.")


@login_required
@user_passes_test(is_teacher)
def teacher(request):

    teacher = request.user.teacher
    teaching_instances = TeachingInstance.objects.filter(teacher=teacher).prefetch_related('course')

    courses = []
    for ti in teaching_instances:
        courses.append(ti.course)

    template = loader.get_template('ComSemApp/teacher/my_courses.html')
    context = {
        'teacher': teacher,
        'courses': courses,
    }
    return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_teacher)
def course_students(request):
    course_id = request.POST.get('course_id', None)

    # is this course id valid?
    teacher = request.user.teacher
    if not teaches_course(teacher, course_id):
        return HttpResponse("Invalid course ID")


    course = Course.objects.get(id=course_id)
    students = Enrollment.objects.filter(course=course).select_related('student')

    template = loader.get_template('ComSemApp/teacher/course_students.html')
    context = {
        'students': students,
    }
    return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_teacher)
def teacher_course(request, course_id):

    # is this course id valid?
    teacher = request.user.teacher
    if not teaches_course(teacher, course_id):
        return HttpResponse("Invalid course ID")


    course = Course.objects.get(id=course_id)
    worksheets = Worksheet.objects.filter(course=course)

    template = loader.get_template('ComSemApp/teacher/course.html')
    context = {
        'course': course,
        'worksheets': worksheets,
    }
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_teacher)
def delete_worksheet(request):
    worksheet_id = request.POST.get('worksheet_id', None)
    worksheet = get_object_or_404(Worksheet, id=worksheet_id)

    # is this course id valid?
    teacher = request.user.teacher
    if not teaches_course(teacher, worksheet.course.id):
        return HttpResponse("Invalid course ID")

    worksheet.delete()

    return HttpResponse(status=204)



@login_required
@user_passes_test(is_teacher)
def release_worksheet(request):
    worksheet_id = request.POST.get('worksheet_id', None)
    worksheet = get_object_or_404(Worksheet, id=worksheet_id)

    # is this course id valid?
    teacher = request.user.teacher
    if not teaches_course(teacher, worksheet.course.id):
        return HttpResponse("Invalid course ID")

    Worksheet.objects.filter(id=worksheet.id).update(released=True)
    return HttpResponse(status=204)


@login_required
@user_passes_test(is_teacher)
def teacher_worksheet(request, course_id, worksheet_id):

    # is this course id valid?
    teacher = request.user.teacher
    if not teaches_course(teacher, course_id):
        return HttpResponse("Invalid course ID")

    course = get_object_or_404(Course, id=course_id)
    students = Enrollment.objects.filter(course=course).select_related('student') # get students in course

    context = {
        'course': course,
        'students': students,
    }

    # if this is an edit
    if worksheet_id != '0':

        worksheet = get_object_or_404(Worksheet, id=worksheet_id)

        if not course.id != course_id:
            return HttpResponse("Invalid course ID")

        # get related expression information and serialize it
        expression_obj = Expression.objects.filter(worksheet=worksheet).prefetch_related('student')
        expressions = list(expression_obj.values())

        print(expressions)

        # need to get name of assigned student seperately
        for i in range(len(expressions)):
            student = expression_obj[i].student
            expressions[i]['student_name'] = str(student) if student else None
            expressions[i]['reformulation_audio'] = False if expressions[i]['reformulation_audio'] == '0' else True

        context['worksheet'] = worksheet
        print(json.dumps(expressions))
        context['expressions'] = json.dumps(expressions)

    template = loader.get_template('ComSemApp/teacher/edit_worksheet.html')
    return HttpResponse(template.render(context, request))



@login_required
@user_passes_test(is_teacher)
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

    # is this course id valid?
    teacher = request.user.teacher
    if not teaches_course(teacher, course_id):
        return HttpResponse("Invalid course ID")

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
            handle_uploaded_file(uploading_ra, int(expression_id))


    return HttpResponse(status=204)


def handle_uploaded_file(f, e):
    id_floor = int(math.floor(e/1000))
    url = 'efs/ExpressionReformulations/' + str(id_floor)
    if not os.path.exists(url):
        os.makedirs(url)
    url += '/' + str(e) + ".mp3"
    with open(url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
