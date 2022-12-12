from urllib import request
import urllib3
from datetime import datetime, date
from dbconnect import getAuth
import requests
import pickle
import os
import pprint
import time
import json
import sqlite3
import pymysql
import sys

urllib3.disable_warnings()


def fetch(category, letter, page, sleep=True):
    if sleep:
        time.sleep(6)
    url = "http://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category="
    url += str(category) + "&alpha=" + str(letter) + "&page=" + str(page)
    try:
        return request.urlopen(
            url, timeout=30).read().decode('ISO-8859-1')
        query = json.loads(request.urlopen(
            url, timeout=30).read().decode('ISO-8859-1'))['items']
        if isinstance(query, list):
            return query
        else:
            return None
    except Exception as e:
        print("Fetch failed: " + str(e))


def pager(category, letterP, saveData=True, savePic=True):
    global categorynames
    stamp = date.today()
    today = stamp.strftime("%Y-%m-%d")
    letter = ['#', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
              'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    for cat in range(0, 42):
        for char in letter:  # open the letter
            if char == '#':
                char = '%23'
            for page in list(range(1, 50)):  # page through

                print("Cat: {0} Letter:'{1}' Page: {2}".format(
                    cat, char, page))

                retries = 0  # counter for break the while
                while True:
                    result = fetch(cat, char, page, True)
                    if isinstance(result, str) and len(result) > 26:
                        break  # valid list
                    elif isinstance(result, str) and len(result) < 30:
                        # print(len(result))
                        #print('Empty page')
                        retries = 3
                        break  # valid, but empty page
                    elif retries == 3:
                        #print('Empty page')
                        break  # not valid, after 3 retry
                    else:
                        retries += 1  # not valid until 3 retry
                        # print(len(result))
                        #print('Resend Query')
                        time.sleep(10)
                if retries == 3:  # just break from the outer for cycle
                    break

                row = []  # stores item data for the database query
                url = "https://localhost:44319/api/items"

                payload = result
                headers = {'Content-Type': 'application/json'}

                response = requests.request(
                    "POST", url, headers=headers, data=payload, verify=False)
                print(response.text)


if __name__ == '__main__':
    try:
        print('Runescape Item Updater v1.0')
        pager(0, "#", False)
    except KeyboardInterrupt:
        savelog('---------------------------')
        savelog('<<< User aborted the script')
