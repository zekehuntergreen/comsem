from django.forms import ModelForm
from .models import *

class WorksheetForm(ModelForm):
    class Meta:
        model = Worksheet
        fields = ['display_original', 'display_reformulation_text', 'display_reformulation_audio', 'display_all_expressions']
