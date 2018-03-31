from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import connection

import nltk
from nltk.data import load

import json
from .models import *

#TODO: is the user a teacher or Admin

@login_required
def corpus_search(request):
    tags = Tag.objects.all()
    template = loader.get_template('ComSemApp/corpus/corpus_search.html')
    return HttpResponse(template.render({'tags': tags}, request))

@login_required
def populate_word_tag(request):
    val = request.POST.get('val', None)
    search_type = request.POST.get('type', None)
    output = request.POST.get('output', None)

    context = {}
    id_list = []
    if(search_type == 'word'):
        template = loader.get_template('ComSemApp/corpus/word_table.html')
        words = Word.objects.filter(form=val)
        context = {'val': val, 'words': words} # for html
        id_list = []
        for word in words:
            id_list.append(word.id)
        json_response = {'val': val, 'id_list': id_list} # for json

    else:
        template = loader.get_template('ComSemApp/corpus/tag_table.html')
        if val == "ALL":
            tags = Tag.objects.all()
        else:
            tags = Tag.objects.filter(tag=val)
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
    sequential_search = request.POST.get('searchType') == '1'
    search_criteria = request.POST.get('searchCriteria', None)

    if not search_criteria:
        return HttpResponse('No search criteria provided', status=401)

    search_criteria = json.loads(search_criteria)

    query = build_query(len(search_criteria) - 1, search_criteria, sequential_search)
    print(query)
    with connection.cursor() as cursor:
        expression_ids = []
        cursor.execute(query)
        for row in cursor.fetchall():
            expression_ids.append(row[0])

    # grab the information we want about the expressions
    expressions = Expression.objects.filter(id__in=expression_ids)

    # for each expression, retag in order to show where the matching word / tag is.
    # TODO
    # for expression in expressions:
    #     tokens = nltk.word_tokenize(expression.expression)
    #     tagged = nltk.pos_tag(tokens)
    #     print (tagged)
    #     for criterion in search_criteria:
    #         print (criterion)
    #         if criterion['type'] == 'tag':
    #             tag = criterion['val']
    #             for word in tagged:
    #                 if word[1] == tag:
    #                     print ("match")

    context = {
        'expressions': expressions,
        'sequential_search': sequential_search,
        'search_criteria': search_criteria,
    }
    template = loader.get_template('ComSemApp/corpus/search_results.html')
    return HttpResponse(template.render(context, request))


# work backwards through the search criteria - we make n - 1 joins (where n = number of search criteria) with n tables that
# select expression ID and position (if sequential search).
def build_query(i, search_criteria, sequential_search):
    current_criteria = search_criteria[i]
    criteria_type = current_criteria['type']
    val = current_criteria['val']
    id_list = current_criteria['id_list']

    # if val isnt valid, id_list isn't a list of int ...

    if i < 0:
        return ""
    else:
        if(criteria_type == "offset"):
            print ("to do")

        select_position = ", SW.Position" if sequential_search else ""
        from_words = ", ComSemApp_word as W " if criteria_type == "tag" else ""

        query = "SELECT SW.expression_id" + select_position + " FROM ComSemApp_sequentialwords AS SW" + from_words

        if i > 0:
            query += ", (" + build_query(i - 1, search_criteria, sequential_search) + ") as Derived" + str(i)

        query += " WHERE "

        if criteria_type == "tag":
            query += " SW.word_id = W.id AND W.tag_id in (" + ','.join([str(id) for id in id_list]) + ") "
        else:
            query += " SW.word_id in (" + ','.join([str(id) for id in id_list]) + ") "

        if i > 0:
            if sequential_search:
                next_position = 1

                # if the next search criteria is an offset, we'll use it here then skip it in the next call.
                if search_criteria[i-1]['type'] == 'offset':
                    next_position += search_criteria[i-1]['val']

                query += "AND SW.position = (Derived" + str(i) + ".position + " + str(next_position) + ") "

            query += "AND SW.expression_id = Derived" + str(i) + ".expression_id "
        return query
