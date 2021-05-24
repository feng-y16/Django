import urllib
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
    # import http
    # http.client.HTTPConnection._http_vsn = 10
    # http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

    import http

    def patch_http_response_read(func):
        def inner(*args):
            try:
                return func(*args)
            except http.client.IncompleteRead as e:
                return e.partial

        return inner

    http.client.HTTPResponse.read = patch_http_response_read(http.client.HTTPResponse.read)
    url_filter = re.compile(r'/recipe/[a-zA-Z0-9-_]+', re.S)
    calories_filter = re.compile(r'[0-9]+(?=Calories)', re.S)
    weight_filter = re.compile(r'[0-9<>]+g|[0-9]+mg', re.S)
    word_filter = re.compile(r'[A-Z][a-z]+', re.S)
    percent_filter = re.compile(r'[0-9]+%', re.S)
    img_url_filter = re.compile(r'https%3A%2F%2Flh[a-zA-Z0-9-_ %.=?]+|https://lh[a-zA-Z0-9-_ %.=/?]+', re.S)
    detailed_url_filter = re.compile(r'(?<=\[Read\sDirections]\()[^\s]+(?=\s"Read)', re.S)
    name_filter = re.compile(r'(?<=\s\s#\s)[^#\[\]]+(?=\s\s\[)', re.S)
    time_filter = re.compile(r'(?<=Ingredients\s\s)[0-9]+[^\s]+(?=\s\s)', re.S)
    description_filter = re.compile(r'(?<=### Description\s\s)[^#]+(?=\s\s###)', re.S)
    nutrition_filter = re.compile(r'(?<=NutritionView More)[a-zA-Z0-9 %<>]+(?= \*)', re.S)
    ingredient_filter = re.compile(r'(?<=SERVINGS\s\s\*\s)[^#]+(?=\s\sDid you )', re.S)
    tag_filter = re.compile(r'(?<=### Recipe Tags\s\s\s\s\*\s)[^#]+(?=\s\s###)', re.S)
    tag_word_filter = re.compile(r'(?<=\[)[^]]+(?=])', re.S)

    headers = {"sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
               "sec-ch-ua-mobile": "?0",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/89.0.4389.82 Safari/537.36",
               }
    with requests.get('https://www.yummly.com/recipes?q=' + query + '&taste-pref-appended=true', headers=headers) as r:
        SERP = html2text(r.content.decode()).replace('\n', '')

    urls = ['https://www.yummly.com' + postfix for postfix in url_filter.findall(SERP)]
    urls = list(dict.fromkeys(urls))[0:url_num]
    recipe_data_list = []
    for url in urls:
        recipe_data = collections.OrderedDict()
        if '"' in url:
            continue
        recipe_data['url'] = url
        with requests.get(url, headers=headers) as r:
            detailed_data = html2text(r.content.decode()).replace('\n', ' ')

        detailed_url = detailed_url_filter.findall(detailed_data)
        if len(detailed_url) > 0:
            if '"' not in detailed_url[0]:
                recipe_data['url'] = detailed_url[0]
            else:
                recipe_data['url'] += '#directions'
        else:
            recipe_data['url'] += '#directions'

        name = name_filter.findall(detailed_data)
        if len(name) > 0:
            recipe_data['name'] = name[0].replace('"', "'")
        else:
            continue

        description = description_filter.findall(detailed_data)
        if len(description) > 0:
            recipe_data['description'] = description[0].replace('"', "'")
        else:
            recipe_data['description'] = ''

        tags = tag_filter.findall(detailed_data)
        if len(tags) > 0:
            recipe_data['tags'] = tag_word_filter.findall(tags[0])
        else:
            recipe_data['tags'] = []

        time_needed = time_filter.findall(detailed_data)
        if len(time_needed) > 0:
            recipe_data['time'] = time_needed[0].lower()
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
            recipe_data['calories'] = calories_filter.findall(nutrition)[0] + 'calories'
            for nutrition_key in ['Sodium', 'Fat', 'Protein', 'Carbs', 'Fiber']:
                try:
                    index = recipe_data['nutrition_keys'].index(nutrition_key)
                    recipe_data[nutrition_key.lower()] = recipe_data['nutrition_weight'][index]
                except ValueError:
                    recipe_data[nutrition_key.lower()] = '-1'
        else:
            recipe_data['nutrition_keys'] = []
            recipe_data['nutrition_percent'] = []
            recipe_data['nutrition_weight'] = []
            recipe_data['calories'] = '-1'
            for nutrition_key in ['sodium', 'fat', 'protein', 'carbs', 'fiber']:
                recipe_data[nutrition_key] = '-1'

        img_url = img_url_filter.findall(detailed_data)
        if len(img_url) > 0:
            recipe_data['img_url'] = urllib.parse.unquote(img_url[0]).replace(' ', '')
        else:
            recipe_data['img_url'] = ''
        insert(recipe_data, sql_connection)
        sql_connection.commit()
        recipe_data_list.append(recipe_data)
    return recipe_data_list


def insert(recipe_data, sql_connection):
    if len(sql_connection.execute(f"SELECT url FROM user_recipe where url='{recipe_data['url']}'").fetchall()) > 0:
        return
    max_id = sql_connection.execute("SELECT MAX(ID) FROM user_recipe").fetchall()
    if max_id[0][0] is None:
        id_next = 0
    else:
        id_next = max_id[0][0] + 1
    tags = ''
    for tag in recipe_data['tags']:
        tags += ',' + tag
    tags = tags[1:].replace('"', "'")
    ingredients = ''
    for ingredient in recipe_data['ingredients']:
        ingredients += ',' + ingredient
    ingredients = ingredients[1:].replace('"', "'")
    command = "INSERT INTO user_recipe (id,name,url,tags,description,ingredients,time," \
              "calories,sodium,fat,protein,carbs,fiber,imgurl) "\
              f"VALUES ({id_next}, " \
              f'"{recipe_data["name"]}", ' \
              f'"{recipe_data["url"]}", ' \
              f'"{tags}", ' \
              f'"{recipe_data["description"]}", ' \
              f'"{ingredients}", ' \
              f'"{recipe_data["time"]}", ' \
              f'"{recipe_data["calories"]}", ' \
              f'"{recipe_data["sodium"]}", ' \
              f'"{recipe_data["fat"]}", '\
              f'"{recipe_data["protein"]}", ' \
              f'"{recipe_data["carbs"]}", ' \
              f'"{recipe_data["fiber"]}", ' \
              f'"{recipe_data["img_url"]}")'
    sql_connection.execute(command)


if __name__ == "__main__":
    yummly_args = parse_args()
    connection = sqlite3.connect('db.sqlite3')
    try:
        connection.execute("DELETE FROM user_recipe")
        connection.commit()
    except sqlite3.OperationalError:
        connection.execute('''CREATE TABLE user_recipe
               (id            INT PRIMARY KEY     NOT NULL,
               name           TEXT                NOT NULL,
               url            TEXT                NOT NULL,
               tags           TEXT,
               description    TEXT,
               ingredients    TEXT,
               time           TEXT,
               calories       TEXT,
               sodium         TEXT,
               fat            TEXT,
               protein        TEXT,
               carbs          TEXT,
               fiber          TEXT,
               imgurl         TEXT);''')
        connection.commit()
    search_yummly(url_num=yummly_args.url_num, sql_connection=connection)
    connection.close()
