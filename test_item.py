from item import Item
from api import Api
import random, os
import unittest
from Config import *
from json import JSONDecodeError
from requests.exceptions import Timeout
from pager import Pager
from time import sleep

class ConfigTest(unittest.TestCase):

    config = Config()
    
    def test_initFile(self):
        self.assertIsInstance(ConfigTest.config.data, dict)

    def test_saveFile(self):
        saveConfig  = Config()
        saveConfig.f = "testfile"
        saveConfig.data="aha"
        saveConfig.save()
        with open(saveConfig.f, 'r') as f:
            result = f.read()
        os.remove(saveConfig.f)
        self.assertEqual(result, '"aha"')

class TestItem(unittest.TestCase):
    validParam = """{"icon":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_sprite.gif?id=7198","icon_large":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_big.gif?id=7198","id":7198,"type":"Food and Drink","typeIcon":"https://www.runescape.com/img/categories/Food and Drink","name":"Admiral pie","description":"Much tastier than a normal fish pie.","current":{"trend":"neutral","price":"2,741"},"today":{"trend":"neutral","price":0},"members":"true"}"""

    invalidParam = """{"icon":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_sprite.gif?id=7198","icon_large":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_big.gif?id=7198","id":"aaaaaaa","type":"Food and Drink","typeIcon":"https://www.runescape.com/img/categories/Food and Drink","name":"asdfasdf","description":"Much tastier than a normal fish pie.","current":{"trend":"neutral","price":"2,741"},"today":{"trend":"neutral","price":0},"members":"true"}"""

    invalidJSON = """"icon:"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_sprite.gif?id=7198","icon_large:"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_big.gif?id=7198","id":"aaaaaaa","type":"Food and Drink","typeIcon":"https://www.runescape.com/img/categories/Food and Drink","name":"asdfasdf","description":"Much tastier than a normal fish pie.","current":{"trend":"neutral","price":"2,741"},"today":{"trend":"neutral","price":0},"members":"true"}"""

    def test_InitialData(self):
    #must contain initialData
        item = Item(self.validParam)
        self.assertTrue(len(item.initialData) > 0)

    def test_InitialData_JSONConversion(self):
        #JSON converted succesfully
        with self.assertRaises(JSONDecodeError):
            Item(self.invalidJSON)
        self.assertRaises(JSONDecodeError) 

    def test_Initialize_with_invalid_data(self):
        # initialized with invalid data

        with self.assertRaises(ValueError):
            Item([])
        self.assertRaises(ValueError) 

    def test_itemQuery_invalid_request(self):
        item = Item(self.validParam)
        self.assertEqual(item.query(""),"Invalid URL")

    def test_get_imageStamp(self):
        #if no class stampId variable, get it
        item = Item(self.validParam)
        item.get_imageStamp()
        self.assertNotEqual(Item.stampId, 0)

    def test_save_sprite(self):
        #test saving the icon
        item = Item(self.validParam)
        try:
            os.remove("/home/adam/repos/rs3GEUpdater/images/small/"+str(item.id)+".gif")
            os.remove("/home/adam/repos/rs3GEUpdater/images/large/"+str(item.id)+".gif")
        except FileNotFoundError:
            pass
        sleep(3)
        item.saveSprite(True,True)
        self.assertTrue(os.path.exists("/home/adam/repos/rs3GEUpdater/images/small/" + str(item.id) + ".gif")
                and os.path.exists("/home/adam/repos/rs3GEUpdater/images/large/" + str(item.id) + ".gif"))

class TestApi(unittest.TestCase):
    api = Api()        
    data = api.cfg.data
    
    def test_getLocalCount(self):
        self.assertIsInstance(TestApi.data['localCount'], int)

    def test_getCategoryCount(self):
        self.assertIsInstance(TestApi.data['localCount'], int)

    def test_cfgData(self):
        self.assertIsInstance(TestApi.data, dict)

    def test_RemoteCount(self):
        self.assertIsInstance(TestApi.data['remoteCount'], int)

    def test_detectRuneDayEqual(self):
        self.assertIsInstance(TestApi.data['lastConfigUpdateRuneday'], int)

    def test_categoryPtr(self):
        self.assertIsInstance(TestApi.data['categoryPtr'], int)

    def test_getSingleCatCount(self):
        self.assertIsInstance(TestApi.api.getSingleCatCount(1), int)

class TestPager(unittest.TestCase):
    pager = Pager()
    data = pager.cfg.data

if __name__ == "__main__":
   unittest.main()
