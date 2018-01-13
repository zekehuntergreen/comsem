from django.forms import ModelForm, Form
from .models import Course, CourseType, Session, SessionType, Teacher, Student
from django.contrib.auth.models import User


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['session', 'course_type', 'teachers', 'students', 'section']

    def __init__(self, *args, **kwargs):
        institution = args[1]
        new_args = [args[0]]
        super(CourseForm, self).__init__(*new_args, **kwargs)
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
        institution = args[1]
        new_args = [args[0]]
        super(SessionForm, self).__init__(*new_args, **kwargs)
        self.fields['session_type'].queryset = SessionType.objects.filter(institution=institution)



class SessionTypeForm(ModelForm):
    class Meta:
        model = SessionType
        fields = ['name', 'order']



class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']

    # def __init__(self, *args, **kwargs):
    #     institution = args[1]
    #     new_args = [args[0]]
    #     super(TeacherForm, self).__init__(*new_args, **kwargs)
    #     self.fields['user'].queryset = User.objects.filter(institution=institution)
