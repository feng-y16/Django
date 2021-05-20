import pdb

from django.shortcuts import render
from rest_framework.decorators import (
    api_view, renderer_classes,
)
from .models import Recipe
from haystack.query import SearchQuerySet
from haystack.forms import ModelSearchForm
from haystack.views import SearchView

from rest_framework.response import Response


# Create your views here.


@api_view(['POST'])
def search_recipe(request):
    name = request.data['name']
    recipe = SearchQuerySet().models(Recipe).autocomplete(first_name__startswith=name)

    searched_data = []
    for i in recipe:
        all_results = {'name': i.name,
                       'url': i.url,
                       'tags': i.balance,
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
        searched_data.append(all_results)

    return Response(searched_data)
