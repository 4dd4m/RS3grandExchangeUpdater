from urllib import request
import requests, re
from datetime import datetime, date
from time import sleep
import os, time, json, sys
from json import JSONDecodeError
from Config import Config


class Api:

    def __init__(self):
       self.localHost = "http://localhost"
       self.cfg = Config()
       self.getLocalCount()
       self.getCategoryCount()
       self.getRemoteCount()
       self.getCategoryPtr()
       self.cfg.save()
       self.lastQuery = ""
       self.lastResponse = ""

    def getCategoryPtr(self):
        #load the category list from config or []
        try:
            return self.cfg.data['categoryPtr']
        except KeyError:
            self.cfg.data['categoryPtr'] = 0

    def getRemoteCount(self):
        #get the number of items from the api
        try:
            return self.cfg.data['remoteCount']
        except KeyError:
            total = 0
            singleCatCount = {}
            for i in range(0,self.cfg.data['categoryCount']):
                singleCatCount[str(i)] = 0
                url = "https://services.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=" + str(i)
                try:
                    sleep(1)
                    response = self.remoteQuery(url).content
                except JSONDecodeError:
                    sleep(10)
                    response = self.remoteQuery(url).content

                for letter in response['alpha']:
                    total += letter['items'] 
                    singleCatCount[str(i)] += letter['items']
                print("Cat: {}. Remote Items:\t{}\tLocal Items\t{}".format(str(i),str(singleCatCount[str(i)]),self.getSingleCatCount(str(i))))
            self.cfg.data['remoteCount'] = total
            self.cfg.data['singleCatCount'] = singleCatCount
            return total

    def getLocalCount(self):
        #get the locally store items from the db
        try:
            return self.cfg.data['localCount']
        except KeyError:
            url = self.localHost + "/count/item"
            count = self.localQuery(url)
            self.cfg.data['localCount'] = count['count']
            return count['count']

    def getCategoryCount(self):
        #get category count from localhsot if not exists in localhost
        try:
            return self.cfg.data['categoryCount']
        except KeyError:
            try:
                url = self.localHost + "/count/category"
                count = self.localQuery(url)
                count = json.loads(response.content)
                self.cfg.data['categoryCount'] = count['count']
                if count['count'] == 0:
                    print("0 Category. Database Seeded?")
                return count['count']
            except JSONDecodeError as e:
                return e

    def getSingleCatCount(self, cat):
        #how many items we have in a category?
        url = self.localHost + "/count/category/" + str(cat)
        data = self.localQuery(url)
        return data['count']

    def remoteQuery(self,url,m="GET"):
        #throw a query to the database
        try:
            sleep(1)
            response = requests.request(url=url,method=m)
            self.lastStatus = response.status_code
            self.lastResponse = json.loads(response.content)
        except UnicodeError:
            self.lastResponse = "Not utf-8 compatible"
            self.lastStatus = "Error"
            print(response.content)
            print(url)
        except:
            self.lastResponse = "Error"
            self.lastStatus = "Error"
            return "Invalid URL"
        self.lastQuery = url
        return json.loads(response.content.decode('ISO-8859-1'))

    def localQuery(self,url,m="GET"):
        #throw a query to the database
        try:
            response = requests.request(url=url,method=m)
        except UnicodeError:
            self.lastResponse = "Not utf-8 compatible"
            self.lastStatus = "Error"
        except:
            self.lastResponse = "Error"
            self.lastStatus = "Error"
            return "Invalid URL"
        self.lastQuery = url
        print(url)
        return json.loads(response.content)

    def get_CatLetterList(self, i):
        url = "https://services.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=" + str(i)
        response = self.remoteQuery(url).content
        response = json.loads(response)
        return response


