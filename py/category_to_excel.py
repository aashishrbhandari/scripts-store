import os
import sys
import pandas as pd
import sqlite3
usage_desc = """
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Script Desc
============

Name: Category To Excel
Created: 12 Dec 2020[Version1],  15 Sep 2021[Version5]
Purpose: To Extract Category and Websites List and Create a Excel Sheet for easy view and access of SafeSquid Web Category
Script Requirement: 
=> Python3 v3.5+ / Python2 v2.7+
=> Python Packages
    :- Pandas
    :- openpyxl


Simple Installation
====================

Step 1: Get This Script, Placed in a Dir

Step 2: Get the Pre-Requistes

    Python2:
    --------
    python2 --version # Should be 2.7.** +
    apt install python-pip # pip is Not Default Found Therefore Download It.
    pip2 install openpyxl pandas # Make sure to use pip2 & download openpyxl & pandas

    Python3:
    --------
    python3 --version # Should be 3.5.** +
    apt-get install python-pip3
    pip3 install openpyxl pandas

Step 3: Run the Script

    Python2:
    --------
    python2 category_to_excel.py # This will use the category.db from the system location


Short Explanation:
==================

1) SafeSquid Stores Category as
   Website Name| All Category It Falls In

2) Data Received From SQLite DB Looks:
   Each Row is received as Tuple and can be Iterated

   ('amazon.com', ',Amazon SIte,')
   ('hdfcbank.com', ',banking,Company Banking Websites,')
   ('dst.com.ng', ',business,Company Blacklisted Websites,Job Search,Storage,')
   ('checkmarx.com', ',business,Company Blacklisted Websites,')
   ('microsoft.com', ',business,COMPANY ALLOWED WEBSITES,')

3) We then Split the Category and create a Unique Set For WebCategory and Any Website which has this in the List is added to that Web Category
Note: We Split it using "," and DO Not Process Any Empty Data

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""


''' Get Data from The Category SQLite DB '''


def get_category_database_set(CATEGORY_DB_PATH):
    CATEGORY_DB_SQL_QUERY = 'SELECT * from PRIVATE_CATEGORY;'

    sqlite3_db_connection = None
    try:
        sqlite3_db_connection = sqlite3.connect(CATEGORY_DB_PATH)
    except Exception as except_me:
        print("Exception Caught", except_me)
        sys.exit(
            "Unable to Connect to Sqlite DB File, Please Check the File & Path Properly")

    db_cursor = sqlite3_db_connection.cursor()
    category_db_result_set = db_cursor.execute(
        CATEGORY_DB_SQL_QUERY).fetchall()
    sqlite3_db_connection.close()  # Close the DB Connection
    return category_db_result_set


""" Start Building the Category JSON """


def build_category_data(category_db):
    category_list = {}
    for one_row in category_db:
        website_name = one_row[0]
        website_category_list = one_row[1]
        for one_category_name in website_category_list.split(','):
            if one_category_name != '':
                if one_category_name in category_list.keys():
                    # Append to Website List, only add if not exists
                    if website_name not in category_list.get(one_category_name):
                        category_list.get(
                            one_category_name).append(website_name)
                else:
                    # Create New WebCategory & Add New Website in the Website List in JSON (Object)
                    category_list[one_category_name] = [website_name]

    return category_list


""" Generate Excel Sheet using OpenPyXL """


def generate_excel(category_list, category_sheet):
    startcol = 0
    writer = pd.ExcelWriter(category_sheet, engine='openpyxl')
    for category_name, category_website_list in category_list.items():
        df = pd.DataFrame({category_name: category_website_list})
        df.to_excel(writer, startcol=startcol, index=False,
                    sheet_name='SafeSquid WebCategory List')
        startcol = startcol + 1
    writer.save()


""" Start The Processing """


def main():
    category_sheet = 'SafeSquid_Category_Sheet.xlsx'
    print(usage_desc)

    category_db_file = None
    if sys.argv > 1:
        category_db_file = os.path.abspath(sys.argv[1])
        print("(File as Arg Provided) Using Category DB File: ", category_db_file)
    else:
        category_db_file = os.path.abspath(
            "/var/lib/safesquid/category/category.db")
        print("(NO!! File as Arg Provided) Using Category DB (DEFAULT) File: ",
              category_db_file)

    category_db_result_set = get_category_database_set(category_db_file)
    category_list = build_category_data(category_db_result_set)
    generate_excel(category_list=category_list, category_sheet=category_sheet)


main()
