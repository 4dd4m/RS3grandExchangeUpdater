import os
import json

class Config:
    def __init__(self):
        self.f = "config"
        self.data = self.initFile()

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

    def save(self):
        with open (self.f, 'w') as f:
            data = json.dumps(self.data)
            f.write(data)
            f.close()
    def __str__(self):
        return self.data
