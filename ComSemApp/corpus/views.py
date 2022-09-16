from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.db import connection

import json
from ComSemApp.models import *

# TODO: is the user a teacher or Admin

@login_required
def corpus_search(request):
    tags = Tag.objects.all()
    template = loader.get_template('ComSemApp/corpus/corpus_search.html')
    return HttpResponse(template.render({'tags': tags, 'offsetRange': [i for i in range(-8, 8+1)]}, request))


@login_required
def populate_word_tag(request):
    val = request.POST.get('val', None).strip()
    search_type = request.POST.get('type', None)
    output = request.POST.get('output', None)

    context = {}
    id_list = []
    if(search_type == 'word'):
        template = loader.get_template('ComSemApp/corpus/word_table.html')
        words = Word.objects.filter(form=val)
        context = {'val': val, 'words': words}  # for html
        id_list = []
        for word in words:
            id_list.append(word.id)
        json_response = {'val': val, 'id_list': id_list}  # for json

    else:
        template = loader.get_template('ComSemApp/corpus/tag_table.html')
        if val == "ALL":
            tags = Tag.objects.all()
        else:
            tags = Tag.objects.filter(tag=val)
        context = {'val': val, 'tags': tags}  # for html
        for tag in tags:
            id_list.append(tag.id)
        json_response = {'val': val, 'id_list': id_list}  # for json

    if output == 'html':
        return HttpResponse(template.render(context, request))
    else:
        return JsonResponse(json_response)


@login_required
def search_results(request):
    sequential_search = request.POST.get('searchType') == '1'
    search_criteria = request.POST.get('searchCriteria', None)

    print(type(search_criteria))

    if not search_criteria:
        return HttpResponse('No search criteria provided', status=401)

    search_criteria = json.loads(search_criteria)

    for item in search_criteria:
        if item['type'] == 'word' and " " in item['val'].rstrip().lstrip():
            return HttpResponse('Invalid input: one word only per entry')

    query = build_query(search_criteria, sequential_search)

    with connection.cursor() as cursor:
        expression_ids = []
        cursor.execute(query)
        for row in cursor.fetchall():
            expression_ids.append(row[0])

    # grab the information we want about the expressions
    expressions = Expression.objects.filter(id__in=expression_ids)

    context = {
        'expressions': expressions,
        'sequential_search': sequential_search,
        'search_criteria': search_criteria,
    }
    template = loader.get_template('ComSemApp/corpus/search_results.html')
    return HttpResponse(template.render(context, request))


# This query builder makes the following assumptions about the search criteria:
# there is one word, either a tag or a second word, and there may be an offset.


def build_query(search_criteria, sequential_search):
    words = []
    tags = []
    offset = 0
    for item in search_criteria:
        if item['type'] == 'word':
            words.append(item)
        elif item['type'] == 'tag':
            tags.append(item)
        elif item['type'] == 'offset' and sequential_search == True:
            offset = item['val']

    if len(words) == 0:
        return ""

    query = "SELECT SW.expression_id"
    if sequential_search:
        query += ", SW.position"
    query += " FROM ComSemApp_sequentialwords as SW"

    if len(words) > 1 or len(tags) > 0:
        query += ", (SELECT SW2.expression_id"
        if sequential_search:
            query += ", SW2.position"
        query += " from ComSemApp_sequentialwords as SW2"
        if len(tags) > 0:
            query += ", ComSemApp_word as W where W.tag_id in (" + ','.join(
                [str(id) for id in tags[0]['id_list']])
            query += ") and SW2.word_id = W.id"
        else:
            query += " where SW2.word_id in (" + ','.join(
                [str(id) for id in words[1]['id_list']])
            query += ")"
        query += ") as derived2"
    query += " where SW.word_id in (" + \
        ','.join([str(id) for id in words[0]['id_list']])
    query += ")"

    if len(words) > 1 or len(tags) > 0:
        query += " and SW.expression_id = derived2.expression_id"

        if offset > 0:
            query += " and derived2.position <= (SW.position + " + str(
                offset) + ") and SW.position < derived2.position"
        elif offset < 0:
            query += " and SW.position <= (derived2.position + " + str(
                abs(offset)) + ") and derived2.position < SW.position"

    return query


# Called when the Error Corpus page is initially being loaded
# On loading, grabs every error category to populate error dropdown as soon as the page loads

@login_required
def error_search(request):
    tags = Tag.objects.all()
    errors = ErrorCategory.objects.all()
    template = loader.get_template('ComSemApp/corpus/error_search.html')
    return HttpResponse(template.render({'tags': tags, 'errors': errors, 'offsetRange': [i for i in range(-8, 8+1)]}, request))


# Ajax called whenever the user selects a new category from the category dropdown.
# Returns every associated sub-category.

@login_required
def subcategories(request):
    error_id = request.GET['error-id']
    result_set = []
    # Get the ErrorCategory object based on the name passed in
    selected_error = ErrorCategory.objects.get(id=error_id)
    # Get every subcategory based on the error name
    all_subcategories = selected_error.errorsubcategory_set.all()
    for subs in all_subcategories:
        result_set.append({'name': subs.subcategory, 'id': subs.id})
    return HttpResponse(json.dumps(result_set), content_type='application/json')


# A request is made to search, so using the criteria passed into us, we'll call and make a query
# and use it in a database search


@login_required
def error_search_results(request):
    category_id = request.POST.get('category_id', None)
    subcategory_id = request.POST.get('subcategory_id', None)

    if not category_id:
        return HttpResponse('No search criteria provided', status=401)
    

    filter_params = {"category": category_id}
    if subcategory_id:
        filter_params["subcategory"] = subcategory_id

    expression_errors = ExpressionError.objects.filter(**filter_params)

    context = {
        'errors': expression_errors,
        # 'search_criteria': search_criteria,
    }
    template = loader.get_template('ComSemApp/corpus/error_search_results.html')
    return HttpResponse(template.render(context, request))

