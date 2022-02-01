from tkinter import E
from django import forms
from ComSemApp.models import Expression

class ExpressionHintForm(forms.Form):
    hint = forms.CharField(widget=forms.Textarea)

ExpressionHintFormset = forms.modelformset_factory(
    Expression,
    extra=0,
    fields=['hint']
)