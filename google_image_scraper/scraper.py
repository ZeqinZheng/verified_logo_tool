import pandas as pd
import ssl
from selenium import webdriver
import urllib.request
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import shutil
import os
import json as json_loader

ssl._create_default_https_context = ssl._create_unverified_context
domains = {}
config = {}
config_keys = ["excel_file_path", "output_folder_path", 
        "start_at", "end_at", "output_file_prefix"]
count = 0

LOGO = "logo"
driver = None
IMG_EXT = ".png"

CONFIG_FILE = "config.json"

def load_parameters():
    if CONFIG_FILE not in os.listdir():
        print("ERROR", CONFIG_FILE, "not found")
        exit(-1)
    with open(CONFIG_FILE, "r") as f:
        js = json_loader.load(f)
        for key in config_keys:
            if key not in js.keys():
                print(f"config file does not have {key}")
                exit(-1)
            config[key] = js[key]
    
    config["output_file_prefix"] = str(config["output_file_prefix"])

    if not os.path.isdir(config["output_folder_path"]):
        print("Invalid output folder path", config["output_folder_path"])
        exit(-1)

    if not config["start_at"]:
        config["start_at"] = 0
    if not config["end_at"]:
        config["end_at"] = 0

    if not str(config["start_at"]).isnumeric() or not str(config["end_at"]).isnumeric():
        print("Invalid start_at || end_at index")
        exit(-1)

    config["start_at"], config["end_at"] = int(config["start_at"]), int(config["end_at"])

def validate_start_end_index(domains):
    if not 0 <= config["start_at"] <= len(domains) or not 0 <= config["end_at"] <= len(domains):
        print("Invalid start_at || end_at index")
        exit(-1)


    #EXCEL_PATH = "/Users/Jm 1/google_image_scraper/extend bank list.xlsx"
    #STORE_PATH = "/Users/Jm 1/Desktop/google_img"
    #prefix = "b"


def get_domains(excel_path):
    try:
        df = pd.read_excel(excel_path, sheet_name="Results")
    except Exception as e:
        print(e)
        exit(-1)
    excel_filename = os.path.basename(excel_path)
    id_column, website_column = "id", "Website address"
    if id_column not in df.columns or website_column not in df.columns:
        print(f"{id_column} or {website_column} does not exist in {excel_filename}")
        exit(-1)
    ids = df[id_column]
    for index, _id in enumerate(ids):
        if _id != 0:
            domains[str(_id)] = df[website_column][index]

def open_chrome():
    global driver
    GOOGLE_IMG_URL = "https://www.google.com.hk/imghp?hl=en-GB"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-notifications")
    #print(chrome_options)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    #driver = webdriver.Chrome(options=chrome_options)
    driver.get(GOOGLE_IMG_URL)

search_bar_xpath = "//input[@title='Search']"
FIRST_IMG_XPATH = "//img[@data-deferred='1']"
SOURCE = "src"

def search_with_keyword(keyword):
    search_bar = driver.find_element_by_xpath(search_bar_xpath)
    search_bar.clear()
    search_bar.send_keys(keyword)
    search_bar.send_keys(Keys.RETURN)

def get_first_img_data():
    try:
        elem = driver.find_element_by_xpath(FIRST_IMG_XPATH)
    except Exception as e:
        print(e)
        return ""
    data = elem.get_attribute(SOURCE)
    return data

def save_img(data, _id, domain_name):
    #filename = config["output_file_prefix"] + _id + IMG_EXT
    filename = _id + IMG_EXT
    try:
        res = urllib.request.urlopen(data)
    except Exception as e:
        print(e)
        return
    if hasattr(res, "file"):
        with open(filename, "wb") as f:
            f.write(res.file.read())
    elif hasattr(res, "content"):
        with open(filename, "wb") as f:
            f.write(res.content)
    else:
        print("Failed to get image from", domain_name)
        return
    global count
    count += 1

load_parameters()
get_domains(config["excel_file_path"])
validate_start_end_index(domains)
os.chdir(config["output_folder_path"])

open_chrome()

start_index, end_index = config["start_at"], config["end_at"] if config["end_at"] != 0 else len(domains)
print(end_index)
for _id in list(domains.keys())[start_index:end_index]:
    keyword = " ".join([domains[_id], LOGO])
    search_with_keyword(keyword)
    data = get_first_img_data()
    if not data:
        driver.close()
        open_chrome()
        search_with_keyword(keyword)
        data = get_first_img_data()
    save_img(data, _id, domains[_id])

driver.close()
print(f"Finished. Totally {count} images collected.")
