from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

import json
from .models import *

#TEST: is the user a teacher or Admin

@login_required
def corpus_search(request):
    template = loader.get_template('ComSemApp/corpus/corpus_search.html')
    return HttpResponse(template.render({}, request))

@login_required
def populate_word_tag(request):
    val = request.POST.get('val', None)
    search_type = request.POST.get('type', None)
    output = request.POST.get('output', None)

    context = {}
    id_list = []
    if(search_type == 'word'):
        template = loader.get_template('ComSemApp/corpus/word_table.html')
        words = Word.objects.filter(form=val).order_by('-frequency')
        context = {'val': val, 'words': words} # for html
        id_list = []
        for word in words:
            id_list.append(word.id)
        json_response = {'val': val, 'id_list': id_list} # for json

    else:
        template = loader.get_template('ComSemApp/corpus/tag_table.html')
        tags = Tag.objects.filter(type=val).order_by('-frequency')
        context = {'val': val, 'tags': tags} # for html
        for tag in tags:
            id_list.append(tag.id)
        json_response = {'val': val, 'id_list': id_list} # for json

    if output == 'html':
        return HttpResponse(template.render(context, request))
    else:
        return JsonResponse(json_response)


@login_required
def search_results(request):
    sequential_search = request.POST.get('searchType')
    search_criteria = request.POST.get('searchCriteria', None)

    if not search_criteria:
        return HttpResponse('No search criteria provided', status=401)

    search_criteria = json.loads(search_criteria)
    # print (search_criteria)
    # print (sequential_search)


    query = build_query(len(search_criteria) - 1, search_criteria, sequential_search)
    print(query)

    return HttpResponse(status=200)


# work backwards through the search criteria - we make n - 1 joins (where n = number of search criteria) with n tables that
# select expression ID and position (if sequential search).
def build_query(i, search_criteria, sequential_search):
    current_criteria = search_criteria[i]
    criteria_type = current_criteria['type']
    val = current_criteria['val']
    id_list = current_criteria['id_list']
    print(i)
    if i < 0:
        return ""
    else:
        if(criteria_type == "offset"):
            print ("to do")

        select_position = ", SW.Position" if sequential_search else ""
        from_words = ", Dictionary as D " if criteria_type == "tag" else ""

        query = "SELECT SW.ExpressionID" + select_position + " FROM SequentialWords AS SW" + from_words

        if i > 0:
            query += ", (" + build_query(i - 1, search_criteria, sequential_search) + ") as Derived" + str(i)

        query += " WHERE "

        if criteria_type == "tag":
            query += " SW.WordID = D.WordID AND D.PoS in (" + ','.join([str(id) for id in id_list]) + ") "
        else:
            query += " SW.WordID in (" + ','.join([str(id) for id in id_list]) + ") "

        if i > 0:
            if sequential_search:
                next_position = 1

                # if the next search criteria is an offset, we'll use it here then skip it in the next call.
                if search_criteria[i-1]['type'] == 'offset':
                    next_position += search_criteria[i-1]['val']

                query += "AND SW.Position = (Derived" + str(i) + ".Position + " + str(next_position) + ") "

            query += "AND SW.ExpressionID = Derived" + str(i) + ".ExpressionID "
        return query
