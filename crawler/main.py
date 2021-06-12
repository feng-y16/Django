import os
import pdb
import sys
import sqlite3
import numpy as np
import threading
import threadpool
import multiprocessing
import requests
import tqdm
import time
import urllib
import imghdr
from yummly import search_yummly


def main_query():
    with open('./static/queries/queries.txt', 'r') as f:
        queries_data = f.readlines()
    # with open('./static/queries/queries.txt', 'w') as f:
    #     f.truncate()
    queries = []
    for query in queries_data:
        query = query.strip()
        if len(query) == 0:
            continue
        target_path = './static/queries/' + query + '.npy'
        if os.path.isfile(target_path):
            continue
        queries.append(query)
    pool = threadpool.ThreadPool(10)
    connection = sqlite3.connect('db.sqlite3', check_same_thread=False)
    with tqdm.tqdm(total=len(queries)) as t:
        def update(_, __):
            t.update(1)
        search_requests = []
        for query in queries:
            target_path = './static/queries/' + query + '.npy'
            search_requests.append(([query, 10, connection, target_path], None))
        search_requests = threadpool.makeRequests(search_yummly, search_requests, update)
        [pool.putRequest(search_request) for search_request in search_requests]
        pool.wait()
    connection.close()
    # recipe_data_list = search_yummly(query=query, url_num=10, sql_connection=connection)


def get_image(url, path):
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)


def main_image():
    connection = sqlite3.connect('db_all.sqlite3', check_same_thread=False)
    info = connection.execute("SELECT id, imgurl FROM user_recipe").fetchall()
    pool = multiprocessing.Pool(10)
    for (id, url) in info:
        path = './static/images/recipes/' + str(id)
        if len(url) == 0:
            continue
        # get_image(url, path)
        pool.apply_async(get_image, [url, path])
    num_jobs = len(pool._cache)
    last_num_jobs = num_jobs
    pool.close()
    with tqdm.tqdm(total=num_jobs) as t:
        while last_num_jobs > 0:
            time.sleep(1)
            current_num_jobs = len(pool._cache)
            if current_num_jobs < last_num_jobs:
                t.update(last_num_jobs - current_num_jobs)
                last_num_jobs = current_num_jobs
    pool.join()
    connection.close()


if __name__ == '__main__':
    main_image()
