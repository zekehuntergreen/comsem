from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q

from .teacher_views import jsonify_expressions, handle_uploaded_file # helpers from theacher views - could be put in seperate module
import json

from .models import *

# DECORATORS
def is_student(user):
    return Student.objects.filter(user=user).exists()

def enrolled_in_course(func):
    def wrapper(request, *args, **kwargs):
        valid = Course.objects.filter(students=request.user.student, id=args[0]).exists()
        if not valid:
            messages.error(request, 'Invalid course ID.')
            return redirect("/student/")
        return func(request, *args, **kwargs)
    return wrapper


# VIEWS
@login_required
@user_passes_test(is_student)
def student(request):
    courses = Course.objects.filter(students=request.user.student)
    template = loader.get_template('ComSemApp/student/my_courses.html')
    return HttpResponse(template.render({'courses': courses}, request))


@login_required
@user_passes_test(is_student)
@enrolled_in_course
def course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    worksheets = Worksheet.objects.filter(course=course, released=True)

    status_colors = {
        "complete": "success",
        "incomplete": "danger",
        "ungraded": "warning",
        "none": "info",
    }
    button_texts = {
        "complete": 'Review Worksheet',
        "incomplete": "Create Submission",
        "ungraded": "Edit Submission",
        "none": "Create Submission",
    }

    # need to get the status of the most recent submission of each worksheet by the student
    for worksheet in worksheets:
        status = "none"
        if StudentSubmission.objects.filter(worksheet_id=worksheet.id).exists():
            latest_submission = StudentSubmission.objects.filter(worksheet_id=worksheet.id).latest()
            status = latest_submission.status

        worksheet.status = status
        worksheet.status_color = status_colors[status]
        worksheet.button_text = button_texts[status]


    template = loader.get_template('ComSemApp/student/course.html')
    context = {
        'course': course,
        'worksheets': worksheets,
    }
    return HttpResponse(template.render(context, request))


@login_required
@user_passes_test(is_student)
def worksheet(request, worksheet_id):
    worksheet = get_object_or_404(Worksheet, id=worksheet_id)

    # not correct
    submissions = StudentSubmission.objects.filter(Q(worksheet=worksheet), Q(student=request.user.student) | Q(student=None) ).prefetch_related('studentattempt_set')

    if submissions:
        latest_submission = submissions[0]
        attempts = latest_submission.studentattempt_set.all()
    else:
        latest_submission = None
        attempts = []

    # add check for assigned to me, everyone, etc
    expression_queryset = Expression.objects.filter(worksheet=worksheet)


    expressions = list(expression_queryset.values())

    # need to get name of assigned student seperately
    for i in range(len(expressions)):
        student = expression_queryset[i].student

        if student:
            if student == request.user.student:
                expressions[i]['student_name'] = "Me"
            else:
                expressions[i]['student_name'] = str(student)
        else:
            expressions[i]['student_name'] = None

        expressions[i]['reformulation_audio'] = False if expressions[i]['reformulation_audio'] == '0' else True

        # need to insert some info into expressions array if this is an edit
        for attempt in attempts:
            if attempt.expression == expression_queryset[i]:
                expressions[i]['correctedExpr'] = attempt.reformulation_text
                expressions[i]['StudentAttemptID'] = attempt.id


    expressions_json = json.dumps(expressions)

    print(expressions_json)

    context = {
        'course': worksheet.course,
        'worksheet': worksheet,
        'submissions': submissions,
        'latest_submission': latest_submission,
        'expressions': expressions_json
    }

    template = loader.get_template('ComSemApp/student/edit_worksheet.html')
    return HttpResponse(template.render(context, request))


def save_submission(request):

    student_submission_id = request.POST.get('studentSubmissionID', 0) # 0 = new submission
    worksheet_id = request.POST.get('worksheetID', None)
    expressions = json.loads(request.POST.get('expressions', None))

    worksheet = get_object_or_404(Worksheet, id=worksheet_id)


    if student_submission_id == '0':
        # new submission - Write to student submissions IF we are not editing an existing one - all submissions start as ungraded
        student_submission = StudentSubmission.objects.create(student=request.user.student, worksheet=worksheet)
    else:
        student_submission = StudentSubmission.objects.get(id=student_submission_id)


    # Write to StudentAttempts whether or not this is a new submission
    for i in range(len(expressions)):
        expression = expressions[i]
        expression_id = expression['id']

        if 'isAltered' in expression:

            # deal with audio reformulation - has the audio been uploaded?
            ra_key = 'audio_ref_' + str(i);
            # either there is an old audio reformulation already saved, or we are saving a new one.
            uploading_ra = request.FILES.get(ra_key, None)
            ra_is_there = True if expression['studentReformulationAudio'] else True if uploading_ra else False

            # this could be an update to an attempt from a previous, ungraded submission. use get_or_create, then update
            attempt, created = StudentAttempt.objects.get_or_create(
                expression=Expression.objects.get(id=expression_id),
                student_submission=student_submission,
            )

            attempt.reformulation_text = expression['correctedExpr']
            attempt.reformulation_audio = ra_is_there
            attempt.save()

            # save the audio reformulation
            if uploading_ra:
                handle_uploaded_file(uploading_ra, "AttemptReformulations", int(attempt.id))


    return HttpResponse(status=204)
