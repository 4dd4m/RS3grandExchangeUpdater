from item import Item
from api import Api
import random, os
import unittest
from Config import *
from json import JSONDecodeError
from requests.exceptions import Timeout
from pager import Pager
from time import sleep

class TestItem(unittest.TestCase):
    validParam = """{"icon":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_sprite.gif?id=7198","icon_large":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_big.gif?id=7198","id":7198,"type":"Food and Drink","typeIcon":"https://www.runescape.com/img/categories/Food and Drink","name":"Admiral pie","description":"Much tastier than a normal fish pie.","current":{"trend":"neutral","price":"2,741"},"today":{"trend":"neutral","price":0},"members":"true"}"""

    invalidParam = """{"icon":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_sprite.gif?id=7198","icon_large":"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_big.gif?id=7198","id":"aaaaaaa","type":"Food and Drink","typeIcon":"https://www.runescape.com/img/categories/Food and Drink","name":"asdfasdf","description":"Much tastier than a normal fish pie.","current":{"trend":"neutral","price":"2,741"},"today":{"trend":"neutral","price":0},"members":"true"}"""

    invalidJSON = """"icon:"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_sprite.gif?id=7198","icon_large:"https://secure.runescape.com/m=itemdb_rs/1649066480707_obj_big.gif?id=7198","id":"aaaaaaa","type":"Food and Drink","typeIcon":"https://www.runescape.com/img/categories/Food and Drink","name":"asdfasdf","description":"Much tastier than a normal fish pie.","current":{"trend":"neutral","price":"2,741"},"today":{"trend":"neutral","price":0},"members":"true"}"""

    on fresh migration will fail
    def test_Item_Should_not_exists_in_the_db(self):
        #must exists in the databse
        item = Item(self.invalidParam)
        self.assertFalse(item.exists)

    def test_Item_Should_exists_in_the_db(self):
        #valid item, but 100% ninexistent item should not exist in the database
        item = Item(self.validParam) 
        self.assertTrue(item.exists)

    def test_add_item_to_db(self):
        #db insertion
        item = Item(self.validParam)
        item.id = random.randint(99999,9999999)
        item.name = "XXXXXXXXXXXXXX"
        item.description = "XXXXXXXXXXXXXX"
        item.toDb()
        self.assertTrue(item.lastStatus == 201 
                and item.lastResponse['status'] == 'The item has been added')

if __name__ == "__main__":
   unittest.main()
