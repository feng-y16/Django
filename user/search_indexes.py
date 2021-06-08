from .models import Recipe
from haystack import indexes


class RecipeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)

    name = indexes.CharField(model_attr='name')
    url = indexes.CharField(model_attr='url')
    tags = indexes.CharField(model_attr='tags', default='')
    description = indexes.CharField(model_attr='description', default='')
    ingredients = indexes.CharField(model_attr='ingredients', default='')
    time = indexes.CharField(model_attr='time', default='-1')
    calories = indexes.CharField(model_attr='calories', default='-1')
    sodium = indexes.CharField(model_attr='sodium', default='-1')
    fat = indexes.CharField(model_attr='fat', default='-1')
    protein = indexes.CharField(model_attr='protein', default='-1')
    carbs = indexes.CharField(model_attr='carbs', default='-1')
    fiber = indexes.CharField(model_attr='fiber', default='-1')
    imgurl = indexes.CharField(model_attr='imgurl', default='')

    def get_model(self):
        return Recipe

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
