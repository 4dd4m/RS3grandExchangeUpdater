from urllib import request
import requests, re
from datetime import datetime, date
from time import sleep
from Api import Api
import os, time, json, sys
from json import JSONDecodeError

class Item(Api):
    stampId=0

    def __init__(self,resultPage,cat=0,letter='#'):
        Api.__init__(self)
        try:
            if isinstance(resultPage, str) == False:
                raise ValueError("Init Param must be STR")
            self.initialData = resultPage
            self.host = "http://localhost"
            self.jason = json.loads(self.initialData)
            self.id = self.jason['id']
            self.type = self.jason['type']
            self.category_id = self.decodeCategory(self.type)
            self.exists = bool(self.isInDb(self.id))
            self.name = self.replaceData(self.jason['name'])
            self.description = self.jason['description']
            self.price = self.jason['current']['price']
            self.members = 1 if self.jason['members'] == 'true' else 0
            self.lastStatus = 0
            self.saveSprite(True,True)
        except JSONDecodeError:
            print("Item couldnt be created from JSoN")
            return None 	

    def decodeCategory(self, category):
        categorynames = ["Miscellaneous", #Categories used by their.index()
                    "Ammo",
                    "Arrows",
                    "Bolts",
                    "Construction materials",
                    "Construction products", #5
                    "Cooking ingredients",
                    "Costumes",
                    "Crafting materials",
                    "Familiars",
                    "Farming produce", #10
                    "Fletching materials",
                    "Food and Drink",
                    "Herblore materials",
                    "Hunting equipment",
                    "Hunting Produce", #15
                    "Jewellery",
                    "Mage armour",
                    "Mage weapons",
                    "Melee armour - low level",
                    "Melee armour - mid level", #20
                    "Melee armour - high level",
                    "Melee weapons - low level",
                    "Melee weapons - mid level",
                    "Melee weapons - high level",
                    "Mining and Smithing", #25
                    "Potions",
                    "Prayer armour",
                    "Prayer materials",
                    "Range armour",
                    "Range weapons", #30
                    "Runecrafting",
                    "Runes, Spells and Teleports",
                    "Seeds",
                    "Summoning scrolls",
                    "Tools and containers", #35
                    "Woodcutting product",
                    "Pocket items",
                    "Stone spirits",
                    "Salvage",
                    "Firemaking products", #40
                    "Archaeology materials",
                    ]
        return categorynames.index(category)


    def toDb(self):
        if self.exists == False:
            host = self.host + "/item"
            method = "POST"
            self.category_id += 1 #sb starts with id 1
            print("ADDED: {0}".format(self.name))
            url = "{0}?apid={1}&name={2}&members={3}&category_id={4}&description={5}&active=1&price={6}".format(host,self.id,self.name,self.members,self.category_id,self.description,self.price)
        else:
            method = "PUT"
            host = self.host + "/item/" + str(self.id)
            self.category_id += 1 #sb starts with id 1
            print("EXISTS: {0}".format(self.name))
            url = "{0}?apid={1}&name={2}&members={3}&category_id={4}&description={5}&active=1&price={6}".format(host,self.id,self.name,self.members,self.category_id,self.description,self.price)
        response = self.localQuery(url, method)
        if response['status'] == "Error":
            raise ValueError("The Api Could not save!")

    def isInDb(self, id):
        ##check whether the item exists in the db
        url = self.host + '/item/exists/' + str(id)
        print(url)
        try:
            response = self.localQuery(url)
            return response['status'] == "Exists"
        except AttributeError as e:
            print(str(e) + " " + url)

    def saveSprite(self,small=True,big=True):
        if Item.stampId == 0:
            self.get_imageStamp()
        smSprite = "https://secure.runescape.com/m=itemdb_rs/{0}_obj_sprite.gif?id={1}".format(Item.stampId, str(self.id))
        lgSprite = "https://secure.runescape.com/m=itemdb_rs/{0}_obj_big.gif?id={1}".format(Item.stampId, str(self.id))

        smSpritePath = "/home/adam/repos/rs3GEUpdater/images/small/" + str(self.id) + ".gif"
        lgSpritePath = "/home/adam/repos/rs3GEUpdater/images/large/" + str(self.id) + ".gif"

        if small: #if the small file doesnt exist, save
            if os.path.exists(smSpritePath) == False:
                query = requests.request(url=smSprite,method="GET").content
                f = open(smSpritePath, "wb")
                with open(smSpritePath, 'wb') as handler:
                    handler.write(query)
                    #print("Icon has been saved")
                f.close()

        if big: #if the small file doesnt exist, save
            if os.path.exists(lgSpritePath) == False:
                query = requests.request(url=lgSprite,method="GET").content
                f = open(lgSpritePath, "wb")
                with open(lgSpritePath, 'wb') as handler:
                    handler.write(query)
                f.close()

    def get_imageStamp(self):
        #parse out the imagestamp from the url
        pageUrl = "https://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category=12&alpha=a&page=1"
        page = self.remoteQuery(pageUrl)
        itemElement = page['items'][0]['icon']
        Item.stampId = re.search(r"\d{13}", itemElement).group()

    def replaceData(self, string):
        string = string.replace('+','_plus_ ')
        string = string.replace('+','_plus_')
        return string

    def __str__(self):
        return "\n\nName: {0}\n-----------------\nId: {1}\nType: {2}\nDescription: {3}\nPrice: {4}\nMembers: {5}\nExists: {6}\nLast Status: {7}\nLast Query: {8}\nLast Response: {9}".format(self.name,self.id,self.type,self.description, self.price,self.members,self.exists,self.lastStatus,self.lastQuery,str(self.lastResponse))
