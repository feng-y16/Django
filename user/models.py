from django.db import models


# Create your models here.
class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, null=False, blank=True)
    url = models.CharField(max_length=50, null=False, blank=True)
    tags = models.CharField(max_length=50, default='', null=True, blank=True)
    description = models.CharField(max_length=50, default='', null=True, blank=True)
    ingredients = models.CharField(max_length=50, default='', null=True, blank=True)
    time = models.CharField(max_length=50, default='-1', null=True, blank=True)
    calories = models.CharField(max_length=50, default='-1', null=True, blank=True)
    sodium = models.CharField(max_length=50, default='-1', null=True, blank=True)
    fat = models.CharField(max_length=50, default='-1', null=True, blank=True)
    protein = models.CharField(max_length=50, default='-1', null=True, blank=True)
    carbs = models.CharField(max_length=50, default='-1', null=True, blank=True)
    fiber = models.CharField(max_length=50, default='-1', null=True, blank=True)
    imgurl = models.CharField(max_length=50, default='', null=True, blank=True)

    def save(self, *args, **kwargs):
        return super(Recipe, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{}:{}".format(self.name, self.url)
