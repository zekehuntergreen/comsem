from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.core.mail import send_mail



from .models import *
from django.contrib.auth.models import User
from .forms import CourseForm, CourseTypeForm, SessionForm, SessionTypeForm, UserForm

# DECORATORS
def is_admin(user):
    return Admin.objects.filter(user=user).exists()

def get_institution(user):
    admin = Admin.objects.get(user=user)
    return admin.institution



@login_required
@user_passes_test(is_admin)
def admin(request):
    context = {}
    template = loader.get_template('ComSemApp/admin/home.html')
    return HttpResponse(template.render(context, request))


# LIST VIEWS
@login_required
@user_passes_test(is_admin)
def teachers(request):
    institution = get_institution(request.user)
    teachers = Teacher.objects.filter(institution=institution)
    template = loader.get_template('ComSemApp/admin/teachers.html')
    return HttpResponse(template.render({'teachers': teachers}, request))

@login_required
@user_passes_test(is_admin)
def students(request):
    institution = get_institution(request.user)
    students = Student.objects.filter(institution=institution)
    template = loader.get_template('ComSemApp/admin/students.html')
    return HttpResponse(template.render({'students': students}, request))

@login_required
@user_passes_test(is_admin)
def courses(request):
    institution = get_institution(request.user)
    course_types = CourseType.objects.filter(institution=institution)
    template = loader.get_template('ComSemApp/admin/courses.html')
    return HttpResponse(template.render({'course_types': course_types}, request))

@login_required
@user_passes_test(is_admin)
def course_types(request):
    institution = get_institution(request.user)
    course_types = CourseType.objects.filter(institution=institution)
    template = loader.get_template('ComSemApp/admin/course_types.html')
    return HttpResponse(template.render({'course_types': course_types}, request))

@login_required
@user_passes_test(is_admin)
def sessions(request):
    institution = get_institution(request.user)
    session_types = SessionType.objects.filter(institution=institution)
    template = loader.get_template('ComSemApp/admin/sessions.html')
    return HttpResponse(template.render({'session_types': session_types}, request))

@login_required
@user_passes_test(is_admin)
def session_types(request):
    institution = get_institution(request.user)
    session_types = SessionType.objects.filter(institution=institution)
    template = loader.get_template('ComSemApp/admin/session_types.html')
    return HttpResponse(template.render({'session_types': session_types}, request))


def get_page_title(obj_type):
    if obj_type == 'course':
        return 'Course'
    if obj_type == 'course_type':
        return 'Course Type'
    if obj_type == 'session':
        return 'Session'
    if obj_type == 'session_type':
        return 'Session Type'
    if obj_type == 'teacher':
        return 'Teacher'
    if obj_type == 'student':
        return 'Student'

def get_model_instance(obj_type, obj_id):
    if obj_type == 'course':
        return Course.objects.get(id=obj_id)
    if obj_type == 'course_type':
        return CourseType.objects.get(id=obj_id)
    if obj_type == 'session':
        return Session.objects.get(id=obj_id)
    if obj_type == 'session_type':
        return SessionType.objects.get(id=obj_id)
    if obj_type == 'teacher':
        teacher = Teacher.objects.get(id=obj_id)
        return teacher.user
    if obj_type == 'student':
        student = Student.objects.get(id=obj_id)
        return student.user

def get_model_form(obj_type, content, instance, institution):
    if obj_type == 'course':
        return CourseForm(content, institution, instance=instance)
    if obj_type == 'course_type':
        return CourseTypeForm(content, instance=instance)
    if obj_type == 'session':
        return SessionForm(content, institution, instance=instance)
    if obj_type == 'session_type':
        return SessionTypeForm(content, instance=instance)
    if obj_type == 'teacher':
        return UserForm(content, instance=instance)
    if obj_type == 'student':
        return UserForm(content, instance=instance)


# UPDATE / NEW
@login_required
@user_passes_test(is_admin)
def edit_obj(request, obj_type, obj_id):
    institution = get_institution(request.user)

    # saving
    if request.method == 'POST':
        if int(obj_id) == 0:
            form = get_model_form(obj_type, request.POST, None, institution)
        else:
            instance = get_model_instance(obj_type, obj_id)
            form = get_model_form(obj_type, request.POST, instance, institution)

        if form.is_valid():


            # IF WE ARE SAVING A USER ...
            if obj_type == 'teacher' or obj_type == 'student':
                save_user(request, obj_type, obj_id, form, institution)

            # any other object
            else:
                new_obj = form.save(commit=False)
                new_obj.institution = institution
                new_obj.save()

            return HttpResponseRedirect('/admin/' + obj_type + 's/')

        else:
            page_title = 'Edit ' + get_page_title(obj_type)

    # displaying form
    else:
        if int(obj_id) == 0:
            form = get_model_form(obj_type, None, None, institution)
            page_title = 'New ' + get_page_title(obj_type)
        else:
            instance = get_model_instance(obj_type, obj_id)
            print(obj_type, obj_id)
            form = get_model_form(obj_type, None, instance, institution)
            page_title = 'Edit ' + get_page_title(obj_type)

    return render(request, 'ComSemApp/standard_form.html', {'form': form, 'page_title': page_title})


def save_user(request, obj_type, obj_id, form, institution):
    # create the user
    user_obj = form.save(commit=False)

    # add a random password and send email if new user
    if int(obj_id) == 0:
        my_password = User.objects.make_random_password()
        user_obj.set_password(my_password)
        print (my_password)

        link = "https://www.comsem.net"
        message = "You have been invited to join Communication Seminar by an administrator for " + institution.name + ".\nIn order to log in, go to " + link + " and use \n\tusername: " + user_obj.username + "\n\tpassword: " + my_password + "\nfrom there you can change your password."
        print (message)


        # send the new user an email
        send_mail(
            'Invitation to Communication Seminar',
            message,
            'signup@comsem.net',
            [user_obj.email],
            fail_silently=False,
        )

    user_obj.save()


    if obj_type == 'teacher':
        obj, created = Teacher.objects.get_or_create(user=user_obj)
        if created:
            obj.institution.add(institution)
    if obj_type == 'student':
        obj, created = Student.objects.get_or_create(user=user_obj, institution=institution)






# DELETE
@login_required
@user_passes_test(is_admin)
def delete_obj(request, obj_type, obj_id):
    # if it is an object related to a user obj, we'll set the user to inactive.
    if obj_type == 'teacher' or obj_type == 'student':
        user = get_model_instance(obj_type, obj_id)
        user.is_active = False
        user.save()
        print('here')

    # else we can delete it
    else:
        obj = get_model_instance(obj_type, obj_id)
        obj.delete()
    return HttpResponseRedirect('/admin/' + obj_type + 's/')
