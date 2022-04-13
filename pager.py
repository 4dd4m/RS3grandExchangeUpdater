from api import Api
import json
from time import sleep
from item import Item
from json import JSONDecodeError

class Pager(Api):

    def __init__(self):
        Api.__init__(self)


    def page(self):
        #category page out
        cat = self.cfg.data['categoryPtr']
        for c in range(cat, self.cfg.data['categoryCount']):
            print("Opening Category " + str(c))
            singleCatCount = self.getSingleCatCount(c)

            pageCounter = 0
            #letter page out
            for l in self.getAlpha():
                print("Opening Letter " + l)

                for i in range(1,50):
                    if l == '#':
                        l = '%23'
                    url = "https://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category={}&alpha={}&page={}".format(c,l,i)
                    sleep(3)
                    try:
                        result  = json.loads(self.query(url).content.decode('ISO-8859-1'))
                    except JSONDecodeError:
                        sleep(10)
                        result  = json.loads(self.query(url).content.decode('ISO-8859-1'))
                    items = result['items']
                    if items == [] or len(items) < 12:
                        print("Empty Page")
                        break
                    else:
                        for item in items:
                            obj = Item(json.dumps(item))
                            obj.toDb()
                        pageCounter += 1
                        result = ""
                        items = ""

                self.cfg.save()
            self.cfg.data['categoryPtr'] += 1
            self.cfg.save()
        self.cfg.data['categoryPtr'] += 1
        self.cfg.save()

    def getAlpha(self):
        return ['#', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
        #return ['p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

if __name__ == '__main__':
    p = Pager()
    try:
        p.page()
    except KeyboardInterrupt:
        p.cfg.save()
