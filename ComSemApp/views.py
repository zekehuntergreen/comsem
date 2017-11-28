from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.http import JsonResponse
import datetime

from .models import *

# TESTS
def is_teacher(user):
    print (user.groups.values())
    return user.groups.filter(name='teacher').exists()

# is user a teacher in the course?
def teaches_course(teacher, course_id):
    return TeachingInstance.objects.filter(teacher=teacher, course_id=course_id).exists()


def index(request):
    return HttpResponse("<b>Communication Seminar</b> index.")


@login_required
def corpus(request):
    return HttpResponse("<b>Corpus Page</b>")


@login_required
@user_passes_test(is_teacher)
def teacher(request):

    teacher = request.user.teacher
    teaching_instances = TeachingInstance.objects.filter(teacher=teacher).prefetch_related('course')

    courses = []
    for ti in teaching_instances:
        course = ti.course
        course.active = course.session.start_date <= datetime.date.today() and course.session.end_date >= datetime.date.today()
        course.status = 'active' if course.active else 'archived'
        courses.append(course)

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
    # students = Enrollment.objects.filter(course=course).select_related('student')

    template = loader.get_template('ComSemApp/teacher/course.html')
    context = {
        'course': course,
        'worksheets': worksheets,
    }
    return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_teacher)
def teacher_worksheet(request, worksheet_id):
    worksheet = get_object_or_404(Worksheet, worksheet_id=worksheet_id)
    course_id = worksheet.course_id

    expressions = serializers.serialize('json', Expression.objects.filter(worksheet_id=worksheet_id))
    enrollments = Enrollment.objects.filter(course_id=course_id)

    template = loader.get_template('ComSemApp/teacher/edit_worksheet.html')
    context = {
        'course_id': course_id,
        'worksheet': worksheet,
        'expressions': expressions,
        'enrollments': enrollments,
    }
    return HttpResponse(template.render(context, request))
