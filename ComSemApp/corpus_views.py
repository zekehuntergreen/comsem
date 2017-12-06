from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from .models import *

#TEST: is the user a teacher or Admin

@login_required
def corpus_search(request):
    template = loader.get_template('ComSemApp/corpus/corpus_search.html')
    return HttpResponse(template.render({}, request))

@login_required
def populate_word_tag(request):
    val = request.POST.get('word_or_tag_val', None)
    word_or_tag = request.POST.get('word_or_tag', None)
    output = request.POST.get('output', None)

    if(word_or_tag == 'word'):
        template = loader.get_template('ComSemApp/corpus/word_table.html')
        words = Word.objects.filter(form=val).order_by('-frequency')
        context = {'words': words}

    else:
        template = loader.get_template('ComSemApp/corpus/tag_table.html')
        tags = Tag.objects.filter(type=val).order_by('-frequency')
        context = {'tags': tags}

    return HttpResponse(template.render(context, request))
