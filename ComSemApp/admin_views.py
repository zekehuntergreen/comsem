from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse_lazy

from django.template import loader
from django.shortcuts import get_object_or_404


from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView

from django.core.mail import send_mail
from django.contrib import messages


from .models import *
from django.contrib.auth.models import User
from .forms import CourseForm, CourseTypeForm, SessionForm, SessionTypeForm, TeacherForm, StudentForm, UserForm

# DECORATORS
def is_admin(user):
    return Admin.objects.filter(user=user).exists()

def get_institution(user):
    admin = Admin.objects.get(user=user)
    return admin.institution



@login_required
@user_passes_test(is_admin)
def admin(request):
    return HttpResponseRedirect('/admin/students/')



class AdminViewMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        self.institution = get_institution(self.request.user)
        return Admin.objects.filter(user=self.request.user).exists()

### LIST

class TeacherList(AdminViewMixin, ListView):
    model = Teacher
    template_name = 'ComSemApp/admin/teacher_list.html'

    def get_queryset(self):
        return Teacher.objects.filter(institution=self.institution)


class StudentList(AdminViewMixin, ListView):
    model = Student
    template_name = 'ComSemApp/admin/student_list.html'

    def get_queryset(self):
        return Student.objects.filter(institution=self.institution)


class CourseList(AdminViewMixin, ListView):
    model = Course
    template_name = 'ComSemApp/admin/course_list.html'

    def get_queryset(self):
        course_types = CourseType.objects.filter(institution=self.institution)
        return Course.objects.filter(course_type__in=course_types)


class CourseTypeList(AdminViewMixin, ListView):
    model = CourseType
    template_name = 'ComSemApp/admin/course_type_list.html'

    def get_queryset(self):
        return CourseType.objects.filter(institution=self.institution)


class SessionList(AdminViewMixin, ListView):
    model = Session
    template_name = 'ComSemApp/admin/session_list.html'

    def get_queryset(self):
        session_types = SessionType.objects.filter(institution=self.institution)
        return Session.objects.filter(session_type__in=session_types)


class SessionTypeList(AdminViewMixin, ListView):
    model = SessionType
    template_name = 'ComSemApp/admin/session_type_list.html'

    def get_queryset(self):
        return SessionType.objects.filter(institution=self.institution)


### CREATE


class UserCreateMixin(AdminViewMixin, FormView):
    template_name = 'ComSemApp/standard_form.html'

    def get(self, request, *args, **kwargs):
        user_form = UserForm()
        user_form.prefix = 'user_form'
        obj_form = self.get_obj_form()
        obj_form.prefix = 'obj_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def form_invalid(self, user_form, obj_form, **kwargs):
        user_form.prefix='user_form'
        obj_form.prefix='obj_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def _send_mail(self, user, password):
        link = "https://www.comsem.net"
        message = ("You have been invited to join Communication Seminar by an administrator for " + self.institution.name + ".\n"
                    "In order to log in, go to " + link + " and use \n"
                    "\tusername: " + user.username + "\n\tpassword: " + password + "\n"
                    "from there you can change your password.")

        send_mail(
            'Invitation to Communication Seminar',
            message,
            'signup@comsem.net',
            [user.email],
            fail_silently=False,
        )


class TeacherCreate(UserCreateMixin):
    success_url = reverse_lazy("admin_teachers")

    def get_obj_form(self):
        return TeacherForm()

    def post(self, request, *args, **kwargs):
        user_form = UserForm(self.request.POST, prefix='user_form')
        obj_form = TeacherForm(self.request.POST, prefix='obj_form')

        if user_form.is_valid() and obj_form.is_valid():
            user = user_form.save()
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()

            teacher = obj_form.save(commit=False)
            teacher.user = user
            obj_form.save()
            teacher.institution.add(self.institution)

            super(TeacherCreate, self)._send_mail(user, password)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(user_form, obj_form, **kwargs)


class StudentCreate(UserCreateMixin):
    success_url = reverse_lazy("admin_students")

    def get_obj_form(self):
        return StudentForm()

    def post(self, request, *args, **kwargs):
        user_form = UserForm(self.request.POST, prefix='user_form')
        obj_form = StudentForm(self.request.POST, prefix='obj_form')

        if user_form.is_valid() and obj_form.is_valid():
            user = user_form.save()
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()

            student = obj_form.save(commit=False)
            student.user = user
            student.institution = self.institution
            obj_form.save()

            super(StudentCreate, self)._send_mail(user, password)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(user_form, obj_form, **kwargs)


class TypeCreateMixin(AdminViewMixin, CreateView):

    def form_valid(self, form):
        form.instance.institution = self.institution
        return super(TypeCreateMixin,self).form_valid(form)


class CourseTypeCreate(TypeCreateMixin):
    success_url = reverse_lazy("admin_course_types")
    template_name = 'ComSemApp/standard_form.html'
    form_class = CourseTypeForm


class SessionTypeCreate(TypeCreateMixin):
    success_url = reverse_lazy("admin_session_types")
    template_name = 'ComSemApp/standard_form.html'
    form_class = SessionTypeForm


class InstanceCreateMixin(AdminViewMixin, CreateView):

    def get_form_kwargs(self):
        kwargs = super(InstanceCreateMixin, self).get_form_kwargs()
        kwargs['institution'] = self.institution
        return kwargs


class CourseCreate(InstanceCreateMixin):
    success_url = reverse_lazy("admin_courses")
    template_name = 'ComSemApp/standard_form.html'
    form_class = CourseForm


class SessionCreate(InstanceCreateMixin):
    success_url = reverse_lazy("admin_sessions")
    template_name = 'ComSemApp/standard_form.html'
    form_class = SessionForm















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
        return get_object_or_404(Course, id=obj_id)
    elif obj_type == 'course_type':
        return get_object_or_404(CourseType, id=obj_id)
    elif obj_type == 'session':
        return get_object_or_404(Session, id=obj_id)
    elif obj_type == 'session_type':
        return get_object_or_404(SessionType, id=obj_id)
    elif obj_type == 'teacher':
        teacher = get_object_or_404(Teacher, id=obj_id)
        return teacher.user
    elif obj_type == 'student':
        student = get_object_or_404(Student, id=obj_id)
        return student.user
    else:
        raise Http404('Object does not exist')

def get_model_form(obj_type, content, instance, institution):
    if obj_type == 'course':
        return CourseForm(content, institution, instance=instance)
    elif obj_type == 'course_type':
        return CourseTypeForm(content, instance=instance)
    elif obj_type == 'session':
        return SessionForm(content, institution, instance=instance)
    elif obj_type == 'session_type':
        return SessionTypeForm(content, instance=instance)
    elif obj_type == 'teacher':
        return UserForm(content, instance=instance)
    elif obj_type == 'student':
        return UserForm(content, instance=instance)
    else:
        raise Http404('Object does not exist')


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
                form.save_m2m()

            messages.success(request, 'The ' + obj_type + ' was saved successfully!')

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

        link = "https://www.comsem.net"
        message = ("You have been invited to join Communication Seminar by an administrator for " + institution.name + ".\n"
                    "In order to log in, go to " + link + " and use \n"
                    "\tusername: " + user_obj.username + "\n\tpassword: " + my_password + "\n"
                    "from there you can change your password.")


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

    # else we can delete it
    else:
        obj = get_model_instance(obj_type, obj_id)
        obj.delete()
    return HttpResponseRedirect('/admin/' + obj_type + 's/')
