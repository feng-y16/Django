import urllib.request
import requests
import time
import os
import json
import numpy as np
import argparse
from html2text import html2text
import collections
from lxml import etree
from bs4 import BeautifulSoup
import sqlite3
import re
import pdb


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--studentID", type=str, default="2020210952")
    parser.add_argument("--save-dir", type=str, default="")
    parser.add_argument("--target-pages-dir", type=str, default="Target_Pages_1,2")
    parser.add_argument("--queries", nargs="+", default=["benefits of running regularly",
                                                         "buy computer screen"])
    parser.add_argument("--descriptions", nargs="+", default=["Want to know the benefits of running regularly",
                                                              "Plan to buy a computer screen in online shops"])
    parser.add_argument("--url-num", type=int, default=10)
    return parser.parse_args()


def search_yummly(query='cheese', url_num=10, sql_connection=None):
    url_filter = re.compile(r'/recipe/[a-zA-Z0-9-_]+', re.S)
    calories_filter = re.compile(r'[0-9]+(?=Calories)', re.S)
    weight_filter = re.compile(r'[0-9]+g|[0-9]+mg', re.S)
    word_filter = re.compile(r'[A-Z][a-z]+', re.S)
    percent_filter = re.compile(r'[0-9]+%', re.S)
    number_filter = re.compile(r'[0-9]+', re.S)
    name_filter = re.compile(r'(?<=\s\s#\s)[^#\[\]]+(?=\s\s\[)', re.S)
    time_filter = re.compile(r'(?<=Ingredients\s\s)[0-9]+[^\s]+(?=\s\s)', re.S)
    description_filter = re.compile(r'(?<=### Description\s\s)[^#]+(?=\s\s###)', re.S)
    nutrition_filter = re.compile(r'(?<=NutritionView More)[a-zA-Z0-9 %]+(?= \*)', re.S)
    ingredient_filter = re.compile(r'(?<=SERVINGS\s\s\*\s)[^#]+(?=\s\sDid you )', re.S)
    tag_filter = re.compile(r'(?<=### Recipe Tags\s\s\s\s\*\s)[^#]+(?=\s\s###)', re.S)
    tag_word_filter = re.compile(r'(?<=\[)[^]]+(?=])', re.S)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/87.0.4280.66 Safari/537.36"}
    SERP = html2text(requests.get('https://www.yummly.com/recipes?q=' + query + '&taste-pref-appended=true',
                                  headers=headers).content.decode()).replace('\n', '')
    urls = ['https://www.yummly.com' + postfix for postfix in url_filter.findall(SERP)]
    urls = list(dict.fromkeys(urls))[0:url_num]
    recipe_data_list = []
    for url in urls:
        recipe_data = collections.OrderedDict()
        recipe_data['url'] = url
        detailed_data = html2text(requests.get(url).content.decode()).replace('\n', ' ')

        name = name_filter.findall(detailed_data)
        if len(name) > 0:
            recipe_data['name'] = name[0]
        else:
            continue

        description = description_filter.findall(detailed_data)
        if len(description) > 0:
            recipe_data['description'] = description[0]
        else:
            recipe_data['description'] = ''

        tags = tag_filter.findall(detailed_data)
        if len(tags) > 0:
            recipe_data['tags'] = tag_word_filter.findall(tags[0])
        else:
            recipe_data['tags'] = []

        time_needed = time_filter.findall(detailed_data)
        if len(time_needed) > 0:
            recipe_data['time'] = number_filter.findall(time_needed[0])[0]
        else:
            recipe_data['time'] = -1

        ingredients = ingredient_filter.findall(detailed_data)
        if len(ingredients) > 0:
            recipe_data['ingredients'] = ingredients[0].split('  * ')
        else:
            recipe_data['ingredients'] = ''

        nutrition = nutrition_filter.findall(detailed_data)
        if len(nutrition) > 0:
            nutrition = nutrition[0].replace(' DV', '')
            recipe_data['nutrition_keys'] = word_filter.findall(nutrition)[1:]
            recipe_data['nutrition_percent'] = percent_filter.findall(nutrition)
            recipe_data['nutrition_weight'] = weight_filter.findall(nutrition)
            recipe_data['calories'] = calories_filter.findall(nutrition)[0]
            for nutrition_key in ['sodium', 'fat', 'protein', 'carbs', 'fiber']:
                try:
                    index = recipe_data['nutrition_keys'].index(nutrition_key)
                    recipe_data[nutrition_key] = number_filter.findall(recipe_data['nutrition_weight'][index])[0]
                except ValueError:
                    recipe_data[nutrition_key] = -1
        else:
            recipe_data['nutrition_keys'] = []
            recipe_data['nutrition_percent'] = []
            recipe_data['nutrition_weight'] = []
            recipe_data['calories'] = -1
            for nutrition_key in ['sodium', 'fat', 'protein', 'carbs', 'fiber']:
                recipe_data[nutrition_key] = -1

        # print(recipe_data)
        # text = requests.get(url)
        # text.encoding = 'utf-8'
        # html = etree.HTML(text.text)
        # path = html.xpath('/html/body/div[3]/div[1]/div[3]/div/div/div/div/div[2]/div[2]/img/@src')
        # soup = BeautifulSoup(text.text, 'lxml')
        insert(recipe_data, sql_connection)
        recipe_data_list.append(recipe_data)
    return recipe_data_list


def insert(recipe_data, sql_connection):
    c = sql_connection.cursor()
    try:
        id = c.execute("SELECT MAX(ID) FROM RECIPE").__next__()[0]
        if id is None:
            id = 0
        else:
            id += 1
    except sqlite3.OperationalError:
        id = 0
    except StopIteration:
        id = 0
    tags = ''
    for tag in recipe_data['tags']:
        tags += ',' + tag
    tags = tags[1:]
    ingredients = ''
    for ingredient in recipe_data['ingredients']:
        ingredients += ',' + ingredient
    ingredients = ingredients[1:]
    command = "INSERT INTO RECIPE (ID,NAME,URL,TAGS,DESCRIPTION,INGREDIENTS,TIME," \
              "CALORIES,SODIUM,FAT,PROTEIN,CARBS,FIBER,IMGURL) "\
              f"VALUES ({id}, '{recipe_data['name']}', '{recipe_data['url']}', '{tags}', " \
              f"'{recipe_data['description']}', '{ingredients}', "\
              f"{recipe_data['time']}, {recipe_data['calories']}, {recipe_data['sodium']}, {recipe_data['fat']}, "\
              f"{recipe_data['protein']}, {recipe_data['carbs']}, {recipe_data['fiber']}, '')"
    try:
        c.execute(command)
    except:
        pdb.set_trace()
    print(id)
    sql_connection.commit()


if __name__ == "__main__":
    args = parse_args()
    connection = sqlite3.connect('../db.sqlite3')
    c = connection.cursor()
    c.execute("delete from RECIPE")
    # c.execute("update sqlitesequence SET seq = 0 where name = 'RECIPE'")
    # c.execute('''CREATE TABLE RECIPE
    #        (ID            INT PRIMARY KEY     NOT NULL,
    #        NAME           TEXT                NOT NULL,
    #        URL            TEXT                NOT NULL,
    #        TAGS           TEXT,
    #        DESCRIPTION    TEXT,
    #        INGREDIENTS    TEXT,
    #        TIME           REAL,
    #        CALORIES       REAL,
    #        SODIUM         REAL,
    #        FAT            REAL,
    #        PROTEIN        REAL,
    #        CARBS          REAL,
    #        FIBER          REAL,
    #        IMGURL         TEXT);''')
    connection.commit()
    search_yummly(url_num=args.url_num, sql_connection=connection)
