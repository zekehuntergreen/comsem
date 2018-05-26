from django import forms
from django.forms import ModelForm
from django.urls import reverse_lazy

from bootstrap3_datetime.widgets import DateTimePicker
from django_select2.forms import Select2MultipleWidget

from django.contrib.auth.models import User
from .models import Course, CourseType, Session, SessionType, Teacher, Student, Institution



class SignupForm(ModelForm):
    first_name = forms.CharField(label="Administrator First Name", max_length=100)
    last_name = forms.CharField(label="Administrator Last Name", max_length=100)
    email = forms.EmailField(label="Administrator Email")

    class Meta:
        model = Institution
        fields = ['name', 'city', 'state_province', 'country']
        labels = {
            "name": "Organization / Institution Name",
            "state_province": "State or Province",
        }



# MODEL FORMS FOR ADMIN SIDE
class CourseForm(ModelForm):

    class Meta:
        model = Course
        fields = ['session', 'course_type', 'teachers', 'students', 'section']
        widgets = {
            'teachers': Select2MultipleWidget,
            'students': Select2MultipleWidget,
        }

    def __init__(self, *args, **kwargs):
        institution = kwargs.pop('institution')
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['session'].queryset = Session.objects.filter(session_type__institution=institution)
        self.fields['course_type'].queryset = CourseType.objects.filter(institution=institution)
        self.fields['teachers'].queryset = Teacher.objects.filter(institution=institution)
        self.fields['students'].queryset = Student.objects.filter(institution=institution)


class CourseTypeForm(ModelForm):
    class Meta:
        model = CourseType
        fields = ['name', 'verbose_name']


class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['session_type', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        institution = kwargs.pop('institution')
        super(SessionForm, self).__init__(*args, **kwargs)
        self.fields['session_type'].queryset = SessionType.objects.filter(institution=institution)
        self.fields['start_date'].widget.attrs['class'] = 'datepicker'
        self.fields['end_date'].widget.attrs['class'] = 'datepicker'



class SessionTypeForm(ModelForm):
    class Meta:
        model = SessionType
        fields = ['name', 'order']


class UserForm(ModelForm):
    send_email = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']


class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        exclude = ['user', 'institution'] # does nothing for now

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['country', 'language']


