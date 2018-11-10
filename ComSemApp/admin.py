from django.contrib import admin
from django.apps import apps
from django.utils.html import format_html
from django.urls import reverse

from ComSemApp.models import Worksheet, Expression

# auto-register all models
app = apps.get_app_config('ComSemApp')


class WorksheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution', 'course', 'created_by', 'date', 'topic', 'status')
    list_filter = ['course__course_type__institution']
    def institution(self, obj):
        return obj.course.course_type.institution
admin.site.register(Worksheet, WorksheetAdmin)


class ExpressionAdmin(admin.ModelAdmin):
    list_display = ('id', 'link_to_worksheet', 'date_created', 'institution', 'student', 'expression', 'audio')
    search_fields = ['student__user__first_name', "student__user__last_name", "expression"]
    list_display_links = ('id', 'link_to_worksheet')
    list_filter = ['worksheet__course__course_type__institution']
    def link_to_worksheet(self, obj):
        link = reverse("admin:ComSemApp_worksheet_change", args=[obj.worksheet.id])
        return format_html('<a href="{}">{}</a>', link, obj.worksheet.id)
    def date_created(self, obj):
        return obj.worksheet.date
    def institution(self, obj):
        return obj.worksheet.course.course_type.institution
admin.site.register(Expression, ExpressionAdmin)


for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
