import selenium
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from collections import OrderedDict
import time
import os
import json
import numpy as np
import argparse
import zipfile


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--studentID", type=str, default="2020210952")
    parser.add_argument("--save-dir", type=str, default="")
    parser.add_argument("--target-pages-dir", type=str, default="Target_Pages_1,2")
    parser.add_argument("--queries", nargs="+", default=["benefits of running regularly",
                                                         "buy computer screen"])
    parser.add_argument("--descriptions", nargs="+", default=["Want to know the benefits of running regularly",
                                                              "Plan to buy a computer screen in online shops"])
    return parser.parse_args()


def get_chrome_options(without_image_and_script=False, headless=False):
    chrome_options = Options()
    if without_image_and_script:
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2,
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--disable-gpu")
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1500x5000")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 HAHA")
    chrome_options.add_argument("log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return chrome_options


def fetch_results_bing(args, query_index, url="https://cn.bing.com/?ensearch=1&FORM=BEHPTB"):
    query = args.queries[query_index]
    driver = webdriver.Chrome(options=get_chrome_options(headless=True))
    driver.get(url)
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "sb_form_q")))
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "sb_form_go")))
    time.sleep(1)
    search_input = driver.find_element_by_id("sb_form_q")
    search_input.send_keys(query)
    time.sleep(1)
    search = driver.find_element_by_id("sb_form_go")
    search.click()
    WebDriverWait(driver, 5).until(ec.title_contains(query))
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "b_results")))
    time.sleep(1)
    png_path = os.path.join(args.save_dir,
                            "TP_BING_" + str(query_index + 1) + "_" + args.studentID + ".png")
    full_html = driver.find_element_by_xpath("/html")
    width = int(full_html.size["width"])
    height = int(full_html.size["height"])
    driver.set_window_size(width, height)
    time.sleep(3)
    driver.get_screenshot_as_file(png_path)
    results = driver.find_element_by_id("b_results").\
                  find_elements_by_class_name("b_algo") + \
              driver.find_element_by_id("b_results").\
                  find_elements_by_class_name("b_module_expansion_control.b_module_head")
    time.sleep(1)
    titles = []
    position_ys = []
    urls = []
    results_to_be_deleted = []
    for result in results:
        if result.rect["y"] == 0:
            results_to_be_deleted.append(result)
        else:
            position_ys.append(result.rect["y"])
    for result in results_to_be_deleted:
        results.remove(result)
    rank_index = np.argsort(np.array(position_ys))
    assert len(rank_index) >= 10
    rank_index = rank_index[0: 10]
    sorted_results = []
    for i in range(10):
        sorted_results.append(results[rank_index[i]])
    SERP_num = 0
    for i in range(10):
        result = sorted_results[i]
        if len(result.find_elements_by_tag_name("h2")) == 1:
            titles.append(result.find_element_by_tag_name("h2").find_element_by_tag_name("a").text)
            urls.append(result.find_element_by_tag_name("h2").find_element_by_tag_name("a").get_attribute("href"))
            SERP_num += 1
        elif len(result.find_elements_by_class_name("b_algo")) == 1:
            titles.append(result.find_element_by_class_name("b_expansion_text.b_1linetrunc").text)
            urls.append(result.find_element_by_class_name("b_algo").find_element_by_tag_name("a").get_attribute("href"))
            SERP_num += 1
        else:
            print("Warning: a link is missing.")
            continue
    print(f"SERP number for BING, query {query_index + 1}: {len(titles)}")
    dict_results = []
    for i in range(len(titles)):
        dict_result = OrderedDict()
        dict_result["rank"] = str(i + 1)
        dict_result["title"] = titles[i]
        dict_result["url"] = urls[i]
        dict_results.append(dict_result)
    json_path = os.path.join(args.save_dir, "SE_BING_" + str(query_index + 1) + "_" + args.studentID + ".json")
    with open(json_path, "w") as f:
        for i in range(len(titles)):
            dict_result = dict_results[i]
            f.write(json.dumps(dict_result))
            if i < len(rank_index) - 1:
                f.write("\n")
                f.write("\n")
    driver.quit()
    driver = webdriver.Chrome(options=get_chrome_options(without_image_and_script=True))
    for i in range(len(titles)):
        driver.get(urls[i])
        time.sleep(1)
        html_path = os.path.join(args.target_pages_dir,
                                 "TP_BING_" + str(query_index + 1) + "_" +
                                 str(i + 1) + "_" + args.studentID + ".html")
        with open(html_path, "wb+") as f:
            f.write(driver.page_source.encode("utf-8"))
    driver.quit()
    return


def fetch_results_sougou(args, query_index, url="https://english.sogou.com/"):
    query = args.queries[query_index]
    driver = webdriver.Chrome(options=get_chrome_options(headless=True))
    driver.get(url)
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "query")))
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "stb")))
    time.sleep(1)
    search_input = driver.find_element_by_id("query")
    search_input.send_keys(query)
    time.sleep(1)
    search_input.send_keys(Keys.ENTER)
    WebDriverWait(driver, 5).until(ec.title_contains(query))
    WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "main")))
    time.sleep(1)
    png_path = os.path.join(args.save_dir,
                            "TP_SOUGOU_" + str(query_index + 1) + "_" + args.studentID + ".png")
    full_html = driver.find_element_by_xpath("/html")
    width = int(full_html.size["width"])
    height = int(full_html.size["height"])
    driver.set_window_size(width, height)
    time.sleep(3)
    driver.get_screenshot_as_file(png_path)
    results = []
    for items in driver.find_elements_by_class_name("vrwrap"):
        results += items.find_elements_by_class_name("vr-title")
    time.sleep(1)
    titles = []
    positions = []
    urls = []
    results_to_be_deleted = []
    for result in results:
        if result.rect["y"] == 0:
            results_to_be_deleted.append(result)
        else:
            positions.append((result.rect["x"], result.rect["y"]))
    for result in results_to_be_deleted:
        results.remove(result)
    rank_index = np.argsort(np.array(positions, dtype=[("x", "f4"), ("y", "f4")]), order=("y", "x"))
    assert len(rank_index) >= 10
    rank_index = rank_index[0: 10]
    sorted_results = []
    for i in range(10):
        sorted_results.append(results[rank_index[i]])
    SERP_num = 0
    for i in range(10):
        result = sorted_results[i]
        if len(result.find_elements_by_tag_name("a")) == 1:
            titles.append(result.find_element_by_tag_name("a").text)
            urls.append(result.find_element_by_tag_name("a").get_attribute("href"))
            SERP_num += 1
        else:
            print("Warning: a link is missing.")
            continue
    print(f"SERP number for SOUGOU, query {query_index + 1}: {len(titles)}")
    dict_results = []
    for i in range(len(titles)):
        dict_result = OrderedDict()
        dict_result["rank"] = str(i + 1)
        dict_result["title"] = titles[i]
        dict_result["url"] = urls[i]
        dict_results.append(dict_result)
    json_path = os.path.join(args.save_dir, "SE_SOUGOU_" + str(query_index + 1) + "_" + args.studentID + ".json")
    with open(json_path, "w") as f:
        for i in range(len(titles)):
            dict_result = dict_results[i]
            f.write(json.dumps(dict_result))
            if i < len(rank_index) - 1:
                f.write("\n")
                f.write("\n")
    driver.quit()
    driver = webdriver.Chrome(options=get_chrome_options(without_image_and_script=True))
    for i in range(len(titles)):
        driver.get(urls[i])
        time.sleep(1)
        html_path = os.path.join(args.target_pages_dir,
                                 "TP_SOUGOU_" + str(query_index + 1) + "_" +
                                 str(i + 1) + "_" + args.studentID + ".html")
        with open(html_path, "wb+") as f:
            f.write(driver.page_source.encode("utf-8"))
    driver.quit()
    return


def save_queries(args):
    json_path = os.path.join(args.save_dir, "QD_2020210952.json")
    with open(json_path, "w") as f:
        for i in range(len(args.queries)):
            dict_result = OrderedDict()
            dict_result["queryNum"] = str(i + 1)
            dict_result["query"] = args.queries[i]
            dict_result["description"] = args.descriptions[i]
            f.write(json.dumps(dict_result))
            if i < len(args.queries) - 1:
                f.write("\n")
                f.write("\n")


def make_zip(source_path, output_path):
    zip_f = zipfile.ZipFile(output_path, "w")
    for d in os.listdir(source_path):
        zip_f.write(source_path + os.sep + d, d)
    zip_f.close()


def main(args):
    save_queries(args)
    if not os.path.isdir(args.target_pages_dir):
        os.makedirs(args.target_pages_dir)
    for query_index in range(len(args.queries)):
        fetch_results_bing(args, query_index)
        fetch_results_sougou(args, query_index)
    make_zip(args.target_pages_dir, os.path.join(args.save_dir, "Target_Pages_1,2.zip"))


if __name__ == "__main__":
    main(parse_args())
