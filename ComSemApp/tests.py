from django.test import TestCase
from .models import *

institution_name = "Test Institution"
course_section = 1
course_type_name = "Course Type"
session_type_name = "Session Type"
session_start_date = '2017-01-01'
session_end_date = '2017-01-02'
session_type_order = 1
username = 'username'
email = 'email@email.com'
password = 'password123'

def create_institution():
    return Institution.objects.create(name=institution_name)

def get_institution():
    return Institution.objects.get(name=institution_name)

def create_course():
    return Course.objects.create(session=create_session(), course_type=create_course_type(), section=course_section)

def create_course_type():
    return CourseType.objects.create(institution=get_institution(), name=course_type_name)

def create_session():
    return Session.objects.create(session_type=create_session_type(), start_date=session_start_date, end_date=session_end_date)

def create_session_type():
    return SessionType.objects.create(institution=get_institution(), name=session_type_name, order=session_type_order)

def create_user():
    return User.objects.create_user(username=username, email=email, password=password)

def create_teacher():
    teacher = Teacher.objects.create(user=create_user())
    teacher.institution.add(create_institution())
    return teacher

class TeacherCoursesTests(TestCase):
    # not logged in
    def test_not_logged_in(self):
        response = self.client.get('/teacher/')
        self.assertEqual(response.status_code, 302)

    # user is not a teacher
    def test_not_teacher(self):
        user = create_user();
        self.client.login(username=username, password=password)
        response = self.client.get('/teacher/')
        self.assertEqual(response.status_code, 302)

    # blank teacher_courses page
    def test_no_courses(self):
        teacher = create_teacher();
        self.client.login(username=username, password=password)
        response = self.client.get('/teacher/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No available courses.")
        self.assertQuerysetEqual(response.context['courses'], [])

    # display one course
    def test_valid_course(self):
        teacher = create_teacher();
        self.client.login(username=username, password=password)

        course = create_course()
        course.teachers.add(teacher)

        response = self.client.get('/teacher/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['courses'],
            ['<Course: ' + str(course) + '>']
        )
