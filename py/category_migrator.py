import sqlite3
from pprint import pprint
import os
import sys

"""
### For Py3 [Packages Required: pandas requests ]

apt-get install python-pip3
pip3 install pandas requests

### For Py2 [Packages Required: pandas requests]

apt-get install python-pip
pip2 install pandas requests

### After Above Commands
### You can Just Run

# It will create a Dir: category_files on same location with Files Named a Category Name and Content as List of Websites in that Category
python3 category_migrator.py 
python2 category_migrator.py # For Py2 Users

# When Providing New Proxy (Where you want to Upload these Categories) ProxyIP:Port
python3 category_migrator.py "192.168.1.253:8080"
python2 category_migrator.py "192.168.1.253:8080" # For Py2 Users

# it will start uploading it to the respective Proxy

# Make sure you have the First Rule, Because inorder to Upload i have to use this group so that Any Authentication does not concern us
"""

import pandas as pd
import requests

DIR = "category_files"

""" Get Data from The Category SQLite DB """


def get_category_database_set():
    # CATEGORY_DB_PATH = 'category.db' # Testing using Client Database File
    CATEGORY_DB_PATH = '/var/lib/safesquid/category/category.db'
    CATEGORY_DB_SQL_QUERY = 'SELECT * from PRIVATE_CATEGORY;'
    sqlite3_db_connection = sqlite3.connect(CATEGORY_DB_PATH)
    db_cursor = sqlite3_db_connection.cursor()
    category_db_result_set = db_cursor.execute(CATEGORY_DB_SQL_QUERY)
    # sqlite3_db_connection.close() # Close the DB Connection [Creates Problem Therefore Omitted]
    return category_db_result_set


""" Start Building the Category JSON """


def build_category_data(category_db_result_set):
    category_list = {}
    for one_row in category_db_result_set:
        website_name = one_row[0]
        website_category_list = one_row[1]
        for one_category_name in website_category_list.split(','):
            if one_category_name != '':
                if one_category_name in category_list.keys():
                    # Append to Website List of Category Already Identified & Added in JSON (Object)
                    if website_name not in category_list.get(one_category_name):
                        category_list.get(
                            one_category_name).append(website_name)
                else:
                    # Create New WebCategory & Add New Website in the Website List in JSON (Object)
                    category_list[one_category_name] = [website_name]
    return category_list


""" Python requests """


def upload_category_file(file_name, proxy_set):
    category_name = file_name.split(".")[0].split("/")[1]
    path_name = "type=websites_file&list=" + category_name
    upload_url = 'http://safesquid.cfg/?handler=upload&'
    # upload_url = 'http://10.0.1.93:81/?handler=upload&' # Testing
    upload_url = upload_url + path_name

    multipart_form_data = {
        path_name: (file_name.split("/")[1], open(file_name, 'rb')),
    }

    custom_headers = {
        'Referer': 'http://safesquid.cfg/',
        'X-Forwarded-For': '127.0.0.1'
    }

    proxy_list = {
        "http": "http://" + proxy_set,
        "https": "http://" + proxy_set,
    }

    response = requests.post(
        upload_url, files=multipart_form_data, proxies=proxy_list, headers=custom_headers)

    return response.text


""" Upload Files """


def upload_all_category_files(proxy_set):
    for one_file in os.listdir(DIR):
        file_name = os.path.join(DIR, one_file)
        print("[->] Uploading Category File: ",
              file_name, ", To Proxy: ", proxy_set)
        result = upload_category_file(file_name, proxy_set)
        if "Successful upload" in result:
            print("[+] File Successfully Upload!!! Category File: ",
                  file_name, ", To Proxy: ", proxy_set)
            print(result)


""" Create Category List Files """


def create_category_files(category_list):
    try:
        os.mkdir(DIR)
    except Exception as except_me:
        print("Dir Present: ", except_me)
        return False
    for category_name, category_website_list in category_list.items():
        with open(os.path.join(DIR, category_name + ".txt"), "w") as outfile:
            outfile.write("\n".join(category_website_list))


""" Start The Processing """


def main():
    category_db_result_set = get_category_database_set()
    category_list = build_category_data(category_db_result_set)

    print("Category List from Sqlite DB")
    pprint(category_list)
    create_category_files(category_list)

    if len(sys.argv) > 1:
        proxy_set = sys.argv[1]
        upload_all_category_files(proxy_set)
    else:
        print(
            "Since No ProxyIP:Port Arg is Empty, File Upload will not Work, Provide ProxyIP:Port Combo[Make Sure to put it that way since no Validation is Done for that]")


main()
