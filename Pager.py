from Api import Api
from Item import Item
import json
from json import JSONDecodeError
from time import sleep

class Pager(Api):

    def __init__(self):
        Api.__init__(self)


    def page(self):
        #category page out
        cat = self.cfg.data['categoryPtr']
        for c in range(cat, self.cfg.data['categoryCount']):
            singleCatCount = self.getSingleCatCount(c)

            #letter page out
            for l in self.getAlpha():
                #page page out
                for i in range(1,50):
                    print("----------------\nC:{} | L:{} | P:{}\n----------------".format(str(c), l, str(i)))
                    if l == '#':
                        l = '%23'
                    url = "https://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category={}&alpha={}&page={}".format(c,l,i)
                    sleep(3)
                    try:
                        result  = self.remoteQuery(url)
                    except JSONDecodeError:
                        sleep(10)
                        result  = self.remoteQuery(url)
                    items = result['items']
                    if items == []:
                        print("Empty Page")
                        break
                    else:
                        for item in items:
                            obj = Item(json.dumps(item))
                            obj.toDb()
                        result = ""
                        items = ""

                self.cfg.save()
            self.cfg.data['categoryPtr'] += 1
            self.cfg.save()
        self.cfg.data['categoryPtr'] += 1
        self.cfg.save()

    def getAlpha(self):
        #return ['#', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    
        return ['p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

if __name__ == '__main__':
    p = Pager()
    try:
        p.page()
    except KeyboardInterrupt:
        p.cfg.save()
