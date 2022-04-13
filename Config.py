import os, json
from json import JSONDecodeError
import requests

class Config:
    def __init__(self):
        self.f = "config"
        self.data = self.initFile()
        #self.getLastRuneDay()

    def initFile(self):
        if os.path.exists(self.f) is False:
            with open(self.f, 'w') as f:
                f.write('{}')
                f.close()
                return json.loads('{}')
        else:
            with open('config', 'r') as f:
                data = json.loads(f.read())
                if data == "":
                    return {}
                else:
                    return data

    def getLastRuneDay(self, save=True):
        print('Get Last RuneDay  '+ str(save))
        #gets and sets the lst tune day to cfg
        url = "https://secure.runescape.com/m=itemdb_rs/api/info.json"
        try:
            #sleep(6)
            runeday = json.loads(requests.request(url=url,method="GET").content)
        except JSONDecodeError:
            self.data['lastConfigUpdateRuneday'] = 0
            print("NOT READABLE JSON!")
        self.data['lastConfigUpdateRuneday'] = runeday['lastConfigUpdateRuneday']
        self.lastRuneDay = runeday['lastConfigUpdateRuneday']

    def save(self):
        with open (self.f, 'w') as f:
            data = json.dumps(self.data)
            f.write(data)
            f.close()
    def __str__(self):
        return self.data
