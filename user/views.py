import pdb
import os

from django.shortcuts import render
from rest_framework.decorators import (
    api_view, renderer_classes,
)
from .models import Recipe
from haystack.query import SearchQuerySet
from haystack.forms import ModelSearchForm
from haystack.views import SearchView

from rest_framework.response import Response
from rest_framework.views import APIView
import django
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from haystack.generic_views import SearchView
import json
from django.http import HttpResponse
import collections

cached_results = collections.OrderedDict()


@csrf_exempt
def search_recipe(request):
    if 'q' in request.GET:
        name = request.GET['q']
        if len(name) == 0:
            return render(request, "search/search.html")
        queries_path = 'static/queries/queries.txt'
        if not os.path.isdir(os.path.dirname(queries_path)):
            os.makedirs(os.path.dirname(queries_path))
        if not os.path.isfile(queries_path):
            with open(queries_path, 'w') as f:
                f.write('')
        with open(queries_path, 'a') as f:
            f.write(f'{name}\n')
        if name in cached_results.keys():
            recipes = cached_results[name]
        else:
            recipes = SearchQuerySet().models(Recipe).exclude(no_such_field='x').filter(content=name)
            cached_results[name] = recipes
            if len(cached_results) > 1000:
                cached_results.pop(cached_results.keys()[0])
        searched_data = []
        for i in recipes:
            i.tags = i.tags.split(',')
            tags = ''
            if len(i.tags) > 5:
                i.tags = i.tags[0:5]
            for tag in i.tags:
                tags += ', ' + tag
            i.tags = tags[2:]
            if len(i.description) > 150:
                i.description = i.description[0:150] + '...'
            recipe = {
                'name': i.name,
                'url': i.url,
                'tags': i.tags,
                'description': i.description,
                'ingredients': i.ingredients,
                'time': i.time,
                'calories': i.calories,
                'sodium': i.sodium,
                'fat': i.fat,
                'protein': i.protein,
                'carbs': i.carbs,
                'fiber': i.fiber,
                'imgurl': i.imgurl,
            }
            searched_data.append(recipe)
        # print(searched_data)
        paginator = Paginator(searched_data, 10)
        page = request.GET.get('page')
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)
        return render(request, "search/search.html", {'query': name, 'page': page})
    else:
        return render(request, "search/search.html")


@csrf_exempt
def autocomplete(request):
    recipes = SearchQuerySet().models(Recipe).exclude(no_such_field='x').filter(content=request.GET.get('q'))[0:5]
    suggestions = [recipe.name for recipe in recipes]
    other_suggestion = SearchQuerySet().models(Recipe).exclude(no_such_field='x').\
        spelling_suggestion(request.GET.get('q'))
    if other_suggestion is not None:
        if len(other_suggestion) > 1 and len(suggestions) < 5:
            suggestions.append(other_suggestions)
    return HttpResponse(json.dumps({'results': suggestions}), content_type='application/json')
