# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

class Administrator(models.Model):
    administrator_id = models.IntegerField(db_column='AdministratorID', primary_key=True)
    roleinstance_id = models.IntegerField(db_column='RoleInstanceID', blank=True, null=True)
    # first_name = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)
    # last_name = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)
    # email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Administrators'


class Claws7(models.Model):
    tag = models.CharField(db_column='Tag', primary_key=True, max_length=50)
    tag_type = models.CharField(db_column='TagType', max_length=50, blank=True, null=True)
    tag_details = models.CharField(db_column='TagDetails', max_length=100, blank=True, null=True)
    frequency = models.IntegerField(db_column='Frequency', blank=True, null=True)

    def __str__(self):
        return self.tag

    class Meta:
        managed = False
        db_table = 'CLAWS7'


class Country(models.Model):
    country_id = models.IntegerField(db_column='CountryID', primary_key=True)
    country = models.CharField(db_column='Country', max_length=50, blank=True, null=True)

    def __str__(self):
        return self.country

    class Meta:
        managed = False
        db_table = 'Country'


# class CourseDetails(models.Model):
#     teachers_classesid = models.IntegerField(db_column='Teachers&ClassesID', primary_key=True)
#     crn = models.IntegerField(db_column='CRN', blank=True, null=True)
#     class_names_id = models.IntegerField(db_column='ClassNamesID')
#     section = models.IntegerField(db_column='Section', blank=True, null=True)
#     instructor = models.IntegerField(db_column='Instructor', blank=True, null=True)
#     sessionid = models.IntegerField(db_column='SessionID')
#     notes = models.CharField(db_column='Notes', max_length=255, blank=True, null=True)
#     time = models.DateTimeField(db_column='Time', blank=True, null=True)
#     location = models.CharField(db_column='Location', max_length=50, blank=True, null=True)
#     ka1 = models.CharField(db_column='KA1', max_length=250, blank=True, null=True)
#     ka2 = models.CharField(db_column='KA2', max_length=250, blank=True, null=True)
#     ka3 = models.CharField(db_column='KA3', max_length=250, blank=True, null=True)
#     assignment1 = models.CharField(db_column='Assignment1', max_length=50, blank=True, null=True)
#     assignment2 = models.CharField(db_column='Assignment2', max_length=50, blank=True, null=True)
#     assignment3 = models.CharField(db_column='Assignment3', max_length=50, blank=True, null=True)
#     assignment4 = models.CharField(db_column='Assignment4', max_length=50, blank=True, null=True)
#     ass1 = models.CharField(db_column='Ass1', max_length=50, blank=True, null=True)
#     ass2 = models.CharField(db_column='Ass2', max_length=50, blank=True, null=True)
#     ass3 = models.CharField(db_column='Ass3', max_length=50, blank=True, null=True)
#     classscheduleid = models.IntegerField(db_column='ClassScheduleID', blank=True, null=True)
#     taskscompleted = models.IntegerField(db_column='TasksCompleted', blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'CourseDetails'


class CourseType(models.Model):
    course_types_id = models.ForeignKey('Course', db_column='CourseTypesID', primary_key=True)
    course_name = models.CharField(db_column='CourseName', max_length=50, blank=True, null=True)
    level = models.CharField(db_column='Level', max_length=50, blank=True, null=True)
    course_type_name = models.CharField(db_column='CourseTypeName', max_length=50, blank=True, null=True)
    common_name = models.CharField(db_column='CommonName', max_length=50, blank=True, null=True)

    def __str__(self):
        return self.course_name

    class Meta:
        managed = False
        db_table = 'CourseTypes'


class Course(models.Model):
    # oldid = models.CharField(db_column='OldID', max_length=50, blank=True, null=True)
    course_types_id = models.ForeignKey('CourseType', db_column='CourseTypesID', blank=True, null=True)
    session_instance_id = models.ForeignKey('SessionInstance', db_column='SessionInstanceID', max_length=50, blank=True, null=True)
    institution_id = models.ForeignKey('Institution', db_column='InstitutionID', max_length=50, blank=True, null=True)
    class_names_id = models.CharField(db_column='ClassNamesID', max_length=50, blank=True, null=True)
    teaching_instance_id = models.OneToOneField('TeachingInstance', db_column='TeachingInstanceID', max_length=10, blank=True, null=True)
    section = models.CharField(db_column='Section', max_length=50, blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)
    course_id = models.AutoField(db_column='CourseID', primary_key=True)

    def __str__(self):
        return self.course_types_id.course_name

    class Meta:
        managed = False
        db_table = 'Courses'


class Dictionary(models.Model):
    word_id = models.IntegerField(db_column='WordID', primary_key=True)
    form = models.CharField(db_column='Form', max_length=50, blank=True, null=True)
    pos = models.CharField(db_column='PoS', max_length=30, blank=True, null=True)
    lemmaid = models.IntegerField(db_column='LemmaID', blank=True, null=True)
    lemmaform = models.CharField(db_column='LemmaForm', max_length=50, blank=True, null=True)
    frequency = models.IntegerField(db_column='Frequency', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Dictionary'


class Word(models.Model):
    form = models.CharField(db_column='Form', max_length=50, blank=True, null=True)
    pos = models.CharField(db_column='PoS', max_length=50, blank=True, null=True)
    frequency = models.DecimalField(db_column='Frequency', max_digits=13, decimal_places=0, blank=True, null=True)

    def __str__(self):
        return self.form

    class Meta:
        managed = False
        db_table = 'WORDS'
        


class Enrollment(models.Model):
    # oldid = models.IntegerField(db_column='OldID', blank=True, null=True)
    student_id = models.ForeignKey('Student', models.DO_NOTHING, db_column='StudentID', blank=True, null=True)
    course_id = models.ForeignKey(Course, models.DO_NOTHING, db_column='CourseID', blank=True, null=True)
    enrollment_id = models.AutoField(db_column='EnrollmentID', primary_key=True)

    class Meta:
        managed = False
        db_table = 'Enrollment'


class Error(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    submenusid = models.IntegerField(db_column='SubmenusID', blank=True, null=True)
    errortype = models.CharField(db_column='ErrorType', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Errors'


class Expression(models.Model):
    expression_id = models.AutoField(db_column='ExpressionID', primary_key=True)
    date = models.DateTimeField(db_column='Date')
    student_id = models.IntegerField(db_column='StudentID', blank=True, null=True)
    enrollment_id = models.IntegerField(db_column='EnrollmentID', blank=True, null=True)
    expression = models.CharField(db_column='Expression', max_length=255, blank=True, null=True)
    pronunciation = models.CharField(db_column='Pronunciation', max_length=50, blank=True, null=True)
    context_vocabulary = models.CharField(db_column='ContextVocabulary', max_length=200, blank=True, null=True)
    course_id = models.IntegerField(db_column='CourseID')
    topic_id = models.IntegerField(db_column='TopicID', blank=True, null=True)
    special = models.CharField(db_column='Special', max_length=10, blank=True, null=True)
    all_do = models.IntegerField(db_column='AllDo', blank=True, null=True)
    selected = models.IntegerField(db_column='Selected', blank=True, null=True)
    corpus_submission_status = models.CharField(db_column='CorpusSubmissionStatus', max_length=50, blank=True, null=True)
    submitted_by = models.IntegerField(db_column='SubmittedBy', blank=True, null=True)
    approved_by = models.IntegerField(db_column='ApprovedBy', blank=True, null=True)
    date_approved = models.DateTimeField(db_column='DateApproved', blank=True, null=True)
    worksheet_id = models.ForeignKey('Worksheet', models.DO_NOTHING, db_column='WorksheetID', blank=True, null=True)
    is_deleted = models.IntegerField(db_column='IsDeleted', blank=True, null=True)
    reformulation_text = models.CharField(db_column='ReformulationText', max_length=255, blank=True, null=True)
    reformulation_audio = models.IntegerField(db_column='ReformulationAudio', blank=True, null=True)

    def __str__(self):
        return self.expression

    class Meta:
        managed = False
        db_table = 'Expressions'


class Institution(models.Model):
    institution_id = models.AutoField(db_column='InstitutionID', primary_key=True)
    institution_name = models.CharField(db_column='InstitutionName', max_length=50, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)
    state_province = models.CharField(db_column='StateProvince', max_length=50, blank=True, null=True)
    country = models.CharField(db_column='Country', max_length=50, blank=True, null=True)

    def __str__(self):
        return self.institution_name

    class Meta:
        managed = False
        db_table = 'Institutions'


class Language(models.Model):
    languageid = models.IntegerField(db_column='LanguageID', primary_key=True)
    # oldid = models.IntegerField(db_column='OldID')
    language = models.CharField(db_column='Language', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Languages'


class Level(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    level = models.CharField(db_column='Level', max_length=50, blank=True, null=True)
    level_description = models.TextField(db_column='Level Description', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Level'


class LevelType(models.Model):
    levelsid = models.IntegerField(db_column='LevelsID', primary_key=True)
    levels = models.CharField(db_column='Levels', max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Levels'


class PoSTaggedExpressions(models.Model):
    id = models.IntegerField(db_column='Id', primary_key=True)
    expressions_id = models.IntegerField(db_column='Expressions_ID', blank=True, null=True)
    taggedexpressions = models.TextField(db_column='TaggedExpressions', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'POSTaggedExpressions'


class RoleInstance(models.Model):
    roleinstance_id = models.AutoField(db_column='RoleInstanceID', primary_key=True)
    # oldid = models.IntegerField(db_column='OldID', blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )
    # user = models.ForeignKey('SiteUser', models.DO_NOTHING, blank=True, null=True)
    institution_id = models.ForeignKey(Institution, models.DO_NOTHING, db_column='InstitutionID', blank=True, null=True)
    teacher_id = models.ForeignKey('Teacher', models.DO_NOTHING, db_column='TeacherID', blank=True, null=True)
    student_id = models.ForeignKey('Student', models.DO_NOTHING, db_column='StudentID', blank=True, null=True)
    administrator_id = models.ForeignKey(Administrator, models.DO_NOTHING, db_column='AdministratorID', blank=True, null=True)

    def __str__(self):
        return self.user.first_name

    class Meta:
        managed = False
        db_table = 'RoleInstances'
        unique_together = (('institution_id', 'user'),)



class SequentialWords(models.Model):
    word_id = models.IntegerField(db_column='WordID', blank=True, null=True)
    expression_id = models.ForeignKey(Expression, models.DO_NOTHING, db_column='ExpressionID', blank=True, null=True)
    position = models.IntegerField(db_column='Position', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SequentialWords'


class SessionInstance(models.Model):
    session_instance_id = models.IntegerField(db_column='SessionInstanceID', primary_key=True)
    session_type_id = models.ForeignKey('SessionType', db_column='SessionTypeID')
    start_date = models.DateTimeField(db_column='StartDate', blank=True, null=True)
    end_date = models.DateTimeField(db_column='EndDate', blank=True, null=True)
    year = models.IntegerField(db_column='Year', blank=True, null=True)

    def __str__(self):
        return self.session_type_id + " " + start_date + " - " + end_date

    class Meta:
        managed = False
        db_table = 'SessionInstance'


class SessionType(models.Model):
    session_type_id = models.IntegerField(db_column='SessionTypeID', primary_key=True)
    default_start_date = models.DateTimeField(db_column='DefaultStartDate', blank=True, null=True)
    default_end_date = models.DateTimeField(db_column='DefaultEndDate', blank=True, null=True)
    institution_id = models.ForeignKey(Institution, models.DO_NOTHING, db_column='InstitutionID')
    session_name = models.CharField(db_column='SessionName', max_length=50)
    order_number = models.IntegerField(db_column='OrderNumber')

    def __str__(self):
        return self.session_name

    class Meta:
        managed = False
        db_table = 'SessionType'


# class SiteUser(models.Model):
#     user_id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=250)
#     password = models.CharField(max_length=250)
#     date_added = models.DateTimeField(blank=True, null=True)
#     date_removed = models.DateTimeField(blank=True, null=True)
#     email = models.CharField(max_length=50, blank=True, null=True)
#     first_name = models.CharField(max_length=50, blank=True, null=True)
#     last_name = models.CharField(max_length=50, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'SiteUsers'


class StudentAttempt(models.Model):
    student_attempt_id = models.AutoField(db_column='StudentAttemptID', primary_key=True)
    expression_id = models.IntegerField(db_column='ExpressionID')
    student_submission_id = models.ForeignKey('StudentSubmission', models.DO_NOTHING, db_column='StudentSubmissionID')
    reformulation_text = models.CharField(db_column='ReformulationText', max_length=255, blank=True, null=True)
    reformulation_audio = models.IntegerField(db_column='ReformulationAudio', blank=True, null=True)
    correct = models.IntegerField(db_column='Correct', blank=True, null=True)

    def __str__(self):
        return str(self.student_attempt_id)

    class Meta:
        managed = False
        db_table = 'StudentAttempts'
        unique_together = (('student_submission_id', 'expression_id'),)


class StudentSubmission(models.Model):
    student_submission_id = models.AutoField(db_column='StudentSubmissionID', primary_key=True)
    enrollment_id = models.IntegerField(db_column='EnrollmentID')
    worksheet_id = models.IntegerField(db_column='WorksheetID')
    date = models.DateTimeField(db_column='Date', blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=10, blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=8, blank=True, null=True)

    def __str__(self):
        return str(self.student_submission_id)

    class Meta:
        managed = False
        db_table = 'StudentSubmissions'


class Student(models.Model):
    student_id = models.AutoField(db_column='StudentID', primary_key=True)
    # oldid = models.IntegerField(db_column='OldID', blank=True, null=True)
    last_name = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)
    first_name = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)
    nickname = models.CharField(db_column='Nickname', max_length=50, blank=True, null=True)
    citizenship = models.IntegerField(db_column='Citizenship', blank=True, null=True)
    language = models.IntegerField(db_column='Language', blank=True, null=True)
    # email = models.CharField(max_length=50, blank=True, null=True)
    # email_alt = models.CharField(max_length=50, blank=True, null=True)
    roleinstance_id = models.IntegerField(db_column='RoleInstanceID', blank=True, null=True)
    # corpusaccesslevel = models.CharField(db_column='CorpusAccessLevel', max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.student_id)

    class Meta:
        managed = False
        db_table = 'Students'


# class SubAnalysis(models.Model):
#     subanalysisid = models.IntegerField(db_column='SubAnalysisID', primary_key=True)
#     expression_id = models.IntegerField(db_column='ExpressionID', blank=True, null=True)
#     submenuid = models.IntegerField(db_column='SubMenuID', blank=True, null=True)
#     submenuitemid = models.IntegerField(db_column='SubmenuItemID', blank=True, null=True)
#     error = models.CharField(db_column='Error', max_length=50, blank=True, null=True)
#     analyst = models.IntegerField(db_column='Analyst', blank=True, null=True)
#     notes = models.CharField(db_column='Notes', max_length=50, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'SubAnalysis'


# class Submenus(models.Model):
#     submenuid = models.IntegerField(db_column='SubMenuID', primary_key=True)
#     submenu = models.CharField(db_column='Submenu', max_length=50, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'Submenus'


# class Subsetexpressions(models.Model):
#     subsetexpressionid = models.IntegerField(db_column='SubsetExpressionID', primary_key=True)
#     worksheetsubid = models.IntegerField(db_column='WorksheetSubID')
#     expression_id = models.IntegerField(db_column='ExpressionID')
#
#     class Meta:
#         managed = False
#         db_table = 'SubsetExpressions'


class Teacher(models.Model):
    teacher_id = models.IntegerField(db_column='TeacherID', primary_key=True)
    # oldid = models.IntegerField(db_column='OldID', blank=True, null=True)
    # first_name = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)
    # last_name = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)
    # ranking = models.CharField(db_column='Ranking', max_length=50, blank=True, null=True)
    # email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)
    roleinstance_id = models.IntegerField(db_column='RoleInstanceID', blank=True, null=True)

    def __str__(self):
        return str(self.teacher_id)

    class Meta:
        managed = False
        db_table = 'Teachers'


class TeachingInstance(models.Model):
    teaching_instance_id = models.IntegerField(db_column='TeachingInstanceID', primary_key=True)
    institution_id = models.ForeignKey('Institution', db_column='InstitutionID', blank=True, null=True)
    teacher_id = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='TeacherID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TeachingInstance'


class Topic(models.Model):
    topic_id = models.AutoField(db_column='TopicID', primary_key=True)
    topic = models.CharField(db_column='Topic', max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Topics'





# class WorksheetSubsets(models.Model):
#     worksheetsubsetid = models.IntegerField(db_column='WorksheetSubsetID', primary_key=True)
#     worksheetid = models.IntegerField(db_column='WorksheetID')
#     enrollment_id = models.IntegerField(db_column='EnrollmentID')
#
#     class Meta:
#         managed = False
#         db_table = 'WorksheetSubsets'


class Worksheet(models.Model):
    worksheet_id = models.AutoField(db_column='WorksheetID', primary_key=True)
    date = models.DateTimeField(db_column='Date', blank=True, null=True)
    course_id = models.ForeignKey(Course, models.DO_NOTHING, db_column='CourseID')
    edit_status = models.CharField(db_column='EditStatus', max_length=50, blank=True, null=True)
    topic_id = models.IntegerField(db_column='TopicID')
    display_original = models.IntegerField(db_column='DisplayOriginal', blank=True, null=True)
    display_text_reformulation = models.IntegerField(db_column='DisplayTextReformulation', blank=True, null=True)
    display_audio_reformulation = models.IntegerField(db_column='DisplayAudioReformulation', blank=True, null=True)
    is_deleted = models.IntegerField(db_column='IsDeleted', blank=True, null=True)
    show_all_expressions = models.IntegerField(db_column='ShowAllExpressions', blank=True, null=True)

    def __str__(self):
        return str(self.worksheet_id)

    class Meta:
        managed = False
        db_table = 'Worksheets'


class Year(models.Model):
    year = models.IntegerField(db_column='Year', blank=True, null=True)
    id = models.IntegerField(db_column='ID', primary_key=True)

    def __str__(self):
        return str(self.year)

    class Meta:
        managed = False
        db_table = 'Year'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'
