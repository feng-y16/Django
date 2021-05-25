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

from haystack.generic_views import SearchView


# class SearchRecipeView(SearchView):
#     """My custom search view."""
#
#     def get_queryset(self):
#         queryset = super(SearchRecipeView, self).get_queryset()
#         # further filter queryset based on some set of criteria
#         return queryset.filter(pub_date__gte=date(2015, 1, 1))
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(MySearchView, self).get_context_data(*args, **kwargs)
#         # do something
#         return context

# Create your views here.

# class SearchRecipeView(APIView):
#
#     def get(self, request, format=None):
#         name = request.GET['q']
#         print(name)
#         recipe = SearchQuerySet().models(Recipe).autocomplete(first_name__startswith=name)
#
#         searched_data = []
#         for i in recipe:
#             all_results = {'name': i.name,
#                            'url': i.url,
#                            'tags': i.balance,
#                            'description': i.description,
#                            'ingredients': i.ingredients,
#                            'time': i.time,
#                            'calories': i.calories,
#                            'sodium': i.sodium,
#                            'fat': i.fat,
#                            'protein': i.protein,
#                            'carbs': i.carbs,
#                            'fiber': i.fiber,
#                            'imgurl': i.imgurl,
#                            }
#             searched_data.append(all_results)
#
#         return Response(searched_data)


# @api_view(['POST'])
def search_recipe(request):
    if 'q' in request.GET:
        name = request.GET['q']
        queries_path = 'static/queries/queries.txt'
        if not os.path.isdir(os.path.dirname(queries_path)):
            os.makedirs(os.path.dirname(queries_path))
        if not os.path.isfile(queries_path):
            with open(queries_path, 'w') as f:
                f.write('')
        with open(queries_path, 'a') as f:
            f.write(f'{name}\n')
        recipes = SearchQuerySet().models(Recipe).exclude(no_such_field='x').filter(content=name)
        searched_data = []
        for i in recipes:
            i.tags = i.tags.split(',')
            tags = ''
            if len(i.tags) > 5:
                i.tags = i.tags[0:5]
            for tag in i.tags:
                tags += ', ' + tag
            i.tags = tags[2:]
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
        return render(request, "search/search.html", {})
    # return Response(searched_data)


# @api_view(['GET'])
# def search_recipe(request):
#     try:
#         name = request.GET['q']
#     except django.crawler.datastructures.MultiValueDictKeyError:
#         return render(request, "search/search.html", {})
#     print(name)
#     recipe = SearchQuerySet().models(Recipe).autocomplete(first_name__startswith=name)
#
#     searched_data = []
#     for i in recipe:
#         all_results = {'name': i.name,
#                        'url': i.url,
#                        'tags': i.balance,
#                        'description': i.description,
#                        'ingredients': i.ingredients,
#                        'time': i.time,
#                        'calories': i.calories,
#                        'sodium': i.sodium,
#                        'fat': i.fat,
#                        'protein': i.protein,
#                        'carbs': i.carbs,
#                        'fiber': i.fiber,
#                        'imgurl': i.imgurl,
#                        }
#         searched_data.append(all_results)
#
#     # return Response(searched_data)
#     return render(request, "search/search.html", {"query": name, "object_list": searched_data})
