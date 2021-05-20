from django.db import models


# Create your models here.
class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=True)
    url = models.CharField(max_length=50, null=False, blank=True)
    tags = models.CharField(max_length=50, default='', null=True, blank=True)
    description = models.CharField(max_length=50, default='', null=True, blank=True)
    ingredients = models.CharField(max_length=50, default='')
    time = models.IntegerField(default='-1')
    calories = models.IntegerField(default='-1')
    sodium = models.IntegerField(default='-1')
    fat = models.IntegerField(default='-1')
    protein = models.IntegerField(default='-1')
    carbs = models.IntegerField(default='-1')
    fiber = models.IntegerField(default='-1')
    imgurl = models.CharField(max_length=50, default='', null=True, blank=True)

    def save(self, *args, **kwargs):
        return super(Recipe, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{}:{}".format(self.name, self.url)
