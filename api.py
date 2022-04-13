from urllib import request
import requests, re
from datetime import datetime, date
from  dbconnect import getAuth
from time import sleep
import pickle, os, pprint, time, json, sys
from json import JSONDecodeError
from Config import Config


class Api:

    def __init__(self):
       self.localHost = "http://localhost"
       self.cfg = Config()
       self.getLastRuneDay()
       self.getLocalCount()
       self.getCategoryCount()
       self.getRemoteCount()
       self.detectRuneDayEqual()
       self.getCategoryPtr()
       self.cfg.save()

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
                    response = json.loads(self.query(url).content)
                except JSONDecodeError:
                    sleep(10)
                    response = json.loads(self.query(url).content)

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
            response = self.query(url)
            count = json.loads(response.content)
            self.cfg.data['localCount'] = count['count']
            return count['count']

    def getCategoryCount(self):
        #get category count from localhsot if not exists in localhost
        try:
            return self.cfg.data['categoryCount']
        except KeyError:
            try:
                url = self.localHost + "/count/category"
                response = self.query(url)
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
        data = json.loads(self.query(url).content)
        return data['count']

    def query(self, url, m="GET"):
        #reutrn content
        print("Query: " + url)
        response = requests.request(url=url,method=m)
        return response

    def get_CatLetterList(self, i):
        url = "https://services.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=" + str(i)
        response = self.query(url).content
        response = json.loads(response)
        return response


    def getLastRuneDay(self, save=True):
        print('Get Last RuneDay')
        #gets and sets the lst tune day to cfg
        url = "https://secure.runescape.com/m=itemdb_rs/api/info.json"
        try:
            #sleep(6)
            runeday = json.loads(self.query(url).content)
        except JSONDecodeError:
            self.cfg.data['lastConfigUpdateRuneday'] = 0
            print("NOT READABLE JSON!")
        self.cfg.data['lastConfigUpdateRuneday'] = runeday['lastConfigUpdateRuneday']
        self.lastRuneDay = runeday['lastConfigUpdateRuneday']
    
    def detectRuneDayEqual(self):
        #if we have the runeday in the cfg file exactly as remote return true
        try:
            #not equal so we need to update
            if self.cfg.data['lastConfigUpdateRuneday'] != self.getLastRuneDay(False):
                self.getLastRuneDay()
            return True
        except KeyError:
            self.getLastRuneDay()
            return True

