from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView, DeleteView
from django.views import View

from django.core.mail import send_mail
from django.core.validators import validate_email
from django.contrib import messages
import csv
import io
import re



from ComSemApp.models import *
from django.contrib.auth.models import User
from ComSemApp.administrator.forms import CourseForm, CourseTypeForm, SessionForm, SessionTypeForm, TeacherForm, StudentForm, UserForm
from ComSemApp.libs.mixins import RoleViewMixin
from django.core.exceptions import ValidationError



class AdminViewMixin(RoleViewMixin):

    role_class = Admin

    def _set_role_obj(self):
        # role_obj self in RoleViewMixin
        self.admin = self.role_obj


class InstanceCreateUpdateMixin(AdminViewMixin):
    # initializes the necessary form, passing the current institution
    # necessary in situations like the Course form which offers course type options specific to an institution
    def get_form_kwargs(self):
        kwargs = super(InstanceCreateUpdateMixin, self).get_form_kwargs()
        kwargs['institution'] = self.institution
        return kwargs


### LIST

class TeacherListView(AdminViewMixin, ListView):
    model = Teacher
    template_name = 'ComSemApp/admin/teacher_list.html'

    def get_queryset(self):
        return Teacher.objects.filter(institution=self.institution)


class StudentListView(AdminViewMixin, ListView):
    model = Student
    template_name = 'ComSemApp/admin/student_list.html'
    success_url = reverse_lazy("administrator:students")
    errors= ["bobo"]

    def _send_email(self, user, password):
        print("EMAIL SENT")
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

    def db_get_or_create_institution(self, **kwargs):
        if self.institution:
            return self.institution

        defaults = {
            "name": "Institution Name",
            "city": "Spokane",
            "state_province": "WA",
            "country": "USA",
        }
        self.institution = Institution.objects.create(**defaults)
        return self.institution

    def db_create_user(self, **kwargs):
        user = User.objects.create(**kwargs)
        password = User.objects.make_random_password()
        print("password")
        print(password)
        user.set_password(password)
        user.save()
        self._send_email(user, password)
        return user

    def db_create_student(self, **kwargs):
        institution = self.db_get_or_create_institution()
        user = self.db_create_user(**kwargs)
        return Student.objects.create(user=user, institution=institution)

    #handle CSV upload
    def post(self, request, *args, **kwargs):
        if (len(request.FILES) > 0): #check to make sure file was uploaded
            csv_file = request.FILES['file']
            file_data = csv_file.read().decode("utf-8")	
            lines = file_data.split("\n")
            rejectedLines = []
            message_content = [""]
            linecount = 0
            rejectcount = 0
            for line in lines:
                if len(line): #make sure line isnt empty
                    fields = line.split(",")
                    okToCreate = True
                    rejected = False
                    linecount += 1
                    if (fields[0] == "" or fields[0] == ""):
                        #end of file
                        break
                    if (fields[0].isalpha() == False or fields[1].isalpha() == False):
                        message = (str(linecount) + " " + fields[0] + " " + fields[1] + " " + fields[2] + "        Invalid First or Last Name \n")
                        message_content.append(message)
            
                        rejectcount += 1
                        rejected = True
                        okToCreate = False
                    for user in Student.objects.filter(institution=self.institution):
                        if(user.user.username== fields[2]):
                            okToCreate = False
                            if (rejected == False):     ##if rejected is false, we need to increment the number of rejects, if its already false, dont increment it but still log error
                                rejectcount += 1
                                rejected = True
                            message = (str(linecount) + " " +  fields[0] + " " + fields[1] + " " + fields[2] + "        Duplicate Email Address \n")
                            message_content.append(message)
                            break
                    
                    # Check if a valid email address
                    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', fields[2])
                    if (match == None):
                        if(rejected == False):
                            rejectcount += 1
                            rejected = True
                        okToCreate = False 
                        message = (str(linecount) + " " + fields[0] + " " + fields[1] + " " + fields[2] + "        Invalid Email Address \n")
                        message_content.append(message)
                    if (okToCreate == True):
                        user = {
                            "first_name": fields[0],
                            "last_name": fields[1],
                            "email": fields[2],
                            "username": fields[2] #using email as username so teacher doesnt need to make usernames for everyone
                        }
                        self.db_create_student(**user)
                        print("student made")
                        print(user)
            message_content.insert(0, ("" +  str((linecount - rejectcount)) + "/" + str(linecount)+ " Accounts created sucessfully\n" + "The below users were not added, Their line numbers are listed to the left \n \n"))
            print("linecount" + str(linecount))
            print("rejected lines" + str(rejectcount))
            message_disp = "".join(message_content)
            messages.add_message(request, messages.ERROR, message_disp)
        return HttpResponseRedirect(self.success_url)
            

    def get_queryset(self):
        
        return Student.objects.filter(institution=self.institution)

    


class CourseListView(AdminViewMixin, ListView):
    model = Course
    template_name = 'ComSemApp/admin/course_list.html'

    def get_queryset(self):
        course_types = CourseType.objects.filter(institution=self.institution)
        return Course.objects.filter(course_type__in=course_types)


class CourseTypeListView(AdminViewMixin, ListView):
    model = CourseType
    template_name = 'ComSemApp/admin/course_type_list.html'

    def get_queryset(self):
        return CourseType.objects.filter(institution=self.institution)


class SessionListView(AdminViewMixin, ListView):
    model = Session
    template_name = 'ComSemApp/admin/session_list.html'

    def get_queryset(self):
        session_types = SessionType.objects.filter(institution=self.institution)
        return Session.objects.filter(session_type__in=session_types)


class SessionTypeListView(AdminViewMixin, ListView):
    model = SessionType
    template_name = 'ComSemApp/admin/session_type_list.html'

    def get_queryset(self):
        return SessionType.objects.filter(institution=self.institution)


### CREATE

class UserMixin(AdminViewMixin, FormView):
    # This mixin is used to create and update teachers and students.
    # A mixin is needed because the teacher and student views combine two forms, the django user form and the form
    # for a student / teacher object.
    template_name = 'ComSemApp/standard_form.html'

    def form_invalid(self, user_form, obj_form, **kwargs):
        user_form.prefix = 'user_form'
        obj_form.prefix = 'obj_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def _send_email(self, user, password):
        print("EMAIL SENT")
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


class UserCreateMixin(UserMixin):

    def get(self, request, *args, **kwargs):
        user_form = UserForm()
        user_form.prefix = 'user_form'
        obj_form = self.get_obj_form()
        obj_form.prefix = 'obj_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def post(self, request, *args, **kwargs):
        user_form = UserForm(self.request.POST, prefix='user_form')
        obj_form = self.get_obj_form()
        if user_form.is_valid() and obj_form.is_valid():
            # create the user object with random password
            user = user_form.save()
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()

            # create the student / teacher
            self.save_obj(obj_form, user)

            super(UserCreateMixin, self)._send_email(user, password)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(user_form, obj_form, **kwargs)


class TeacherCreateView(UserCreateMixin):
    success_url = reverse_lazy("administrator:teachers")

    def get_obj_form(self):
        return TeacherForm(self.request.POST, prefix='obj_form')

    def save_obj(self, obj_form, user):
        obj = obj_form.save(commit=False)
        obj.user = user
        obj_form.save()
        obj.institution.add(self.institution)


class StudentCreateView(UserCreateMixin):
    success_url = reverse_lazy("administrator:students")

    def get_obj_form(self):
        return StudentForm(self.request.POST, prefix='obj_form')

    def save_obj(self, obj_form, user):
        obj = obj_form.save(commit=False)
        obj.user = user
        obj.institution = self.institution
        obj_form.save()


class TypeCreateMixin(AdminViewMixin, CreateView):

    def form_valid(self, form):
        form.instance.institution = self.institution
        return super(TypeCreateMixin,self).form_valid(form)


class CourseTypeCreateView(TypeCreateMixin):
    success_url = reverse_lazy("administrator:course_types")
    template_name = 'ComSemApp/standard_form.html'
    form_class = CourseTypeForm


class SessionTypeCreateView(TypeCreateMixin):
    success_url = reverse_lazy("administrator:session_types")
    template_name = 'ComSemApp/standard_form.html'
    form_class = SessionTypeForm


class CourseCreateView(InstanceCreateUpdateMixin, CreateView):
    success_url = reverse_lazy("administrator:courses")
    template_name = 'ComSemApp/standard_form.html'
    form_class = CourseForm


class SessionCreateView(InstanceCreateUpdateMixin, CreateView):
    success_url = reverse_lazy("administrator:sessions")
    template_name = 'ComSemApp/standard_form.html'
    form_class = SessionForm


### UPDATE


class UserUpdateMixin(UserMixin):

    def get(self, request, *args, **kwargs):
        obj_form = self.get_obj_form()
        obj_form.prefix = 'obj_form'
        user_form = UserForm(instance=self.instance.user)
        user_form.prefix = 'user_form'
        return self.render_to_response(self.get_context_data(form=user_form, obj_form=obj_form))

    def post(self, request, *args, **kwargs):
        user_form = UserForm(self.request.POST, instance=self.instance.user, prefix='user_form')
        obj_form = self.get_obj_form(initial=self.request.POST)

        if user_form.is_valid() and obj_form.is_valid():
            user = user_form.save()
            obj_form.save()

            # to do ! what should we send in an email ?
            # super(UserUpdateMixin, self)._send_email(user, password)
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(user_form, obj_form, **kwargs)


class TeacherUpdateView(UserUpdateMixin):
    success_url = reverse_lazy("administrator:teachers")

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Teacher, pk=kwargs['pk'])
        return super(TeacherUpdateView, self).dispatch(request, args, kwargs)

    def get_obj_form(self, initial=None):
        return TeacherForm(initial, instance=self.instance, prefix='obj_form')


class StudentUpdateView(UserUpdateMixin):
    success_url = reverse_lazy("administrator:students")

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Student, pk=kwargs['pk'])
        return super(StudentUpdateView, self).dispatch(request, args, kwargs)

    def get_obj_form(self, initial=None):
        return StudentForm(initial, instance=self.instance, prefix='obj_form')


class CourseTypeUpdateView(AdminViewMixin, UpdateView):
    success_url = reverse_lazy("administrator:course_types")
    model = CourseType
    form_class = CourseTypeForm
    template_name = 'ComSemApp/standard_form.html'


class SessionTypeUpdateView(AdminViewMixin, UpdateView):
    success_url = reverse_lazy("administrator:session_types")
    model = SessionType
    form_class = SessionTypeForm
    template_name = 'ComSemApp/standard_form.html'


class CourseUpdateView(InstanceCreateUpdateMixin, UpdateView):
    success_url = reverse_lazy("administrator:courses")
    model = Course
    form_class = CourseForm
    template_name = 'ComSemApp/standard_form.html'


class SessionUpdateView(InstanceCreateUpdateMixin, UpdateView):
    success_url = reverse_lazy("administrator:sessions")
    model = Session
    form_class = SessionForm
    template_name = 'ComSemApp/standard_form.html'


### DELETE

class NoConfirmDeleteMixin(DeleteView):

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DisactivateUserMixin(NoConfirmDeleteMixin):

    def post(self, request, *args, **kwargs):
        user = self.get_object().user
        user.is_active = False
        user.save()
        return  HttpResponseRedirect(self.success_url)


class TeacherDisactivateView(DisactivateUserMixin):
    success_url = reverse_lazy("administrator:teachers")
    model = Teacher


class StudentDisactivateView(DisactivateUserMixin):
    success_url = reverse_lazy("administrator:students")
    model = Student


class CourseTypeDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:course_types")
    model = CourseType


class SessionTypeDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:session_types")
    model = SessionType


class CourseDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:courses")
    model = Course


class SessionDeleteView(NoConfirmDeleteMixin):
    success_url = reverse_lazy("administrator:sessions")
    model = Session

