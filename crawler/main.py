import os
import pdb
import sys
import sqlite3
import numpy as np
from yummly import search_yummly


def main():
    with open('./static/queries/queries.txt', 'r') as f:
        queries = f.readlines()
    with open('./static/queries/queries.txt', 'w') as f:
        f.truncate()
    for query in queries:
        query = query.strip()
        target_path = './static/queries/' + query + '.npy'
        if os.path.isfile(target_path):
            continue
        connection = sqlite3.connect('db.sqlite3')
        recipe_data_list = search_yummly(query=query, url_num=10, sql_connection=connection)
        np.save(target_path, np.array(recipe_data_list))


if __name__ == '__main__':
    main()
