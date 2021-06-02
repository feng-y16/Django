import os
import pdb
import sys
import sqlite3
import numpy as np
import threading
import threadpool
import tqdm
import time
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


def main_image():
    connection = sqlite3.connect('db.sqlite3', check_same_thread=False)
    urls = connection.execute("SELECT URL FROM user_recipe").fetchall()
    pool = threadpool.ThreadPool(10)
    with tqdm.tqdm(total=len(queries)) as t:
        def update(_, __):
            t.update(1)
        image_requests = []
        for url in urls:
            image_requests.append([url, './static/images/' + url])
        search_requests = threadpool.makeRequests(search_yummly, image_requests, update)
        [pool.putRequest(search_request) for search_request in search_requests]
        pool.wait()
    connection.close()


if __name__ == '__main__':
    main_query()
