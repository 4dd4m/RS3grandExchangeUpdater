from urllib import request
from datetime import datetime, date
from  dbconnect import getAuth
import pickle, os, pprint, time, json, sqlite3, pymysql, sys

"""Connects to a database and returns a cursor"""
#database credentials
auth = getAuth()
host     = auth['host']
database = auth['database']
username = auth['username']
password = auth['password']
table    = auth['table']
try:
    #Initialize db connection
    db = pymysql.connect(host=host,user=username,password=password,database=database,autocommit=True)
    c = db.cursor()
    print("Databse Connected Established...")
    print("Database: {0}".format(database))
    print("Table: {0}".format(table))
    print("User: {0}".format(username))
    #Create Table if it is not exists
    query = """CREATE TABLE IF NOT EXISTS `apidb` (
                      `id` smallint(5) unsigned NOT NULL,
                      `name` varchar(46) DEFAULT NULL,
                      `description` varchar(200) DEFAULT NULL,
                      `members` int(1) NOT NULL,
                      `category` int(2) NOT NULL,
                      `active` BOOLEAN,
                      `updated` date NOT NULL,
                      `added` date NOT NULL,
                      PRIMARY KEY (`id`)
                    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;"""
    c.execute(query)
except pymysql.Error as e: #If not, erormsg
    print(e.args[1])

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
                    "Food and drink",
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
                    "Stone Spirits",
                    "Salvage",
                    "Firemaking products", #40
                    "Archaeology materials",
                    ]

def is_indb(item,today):
    member = ['false','true']
    #query the db if it is exists
    indb = c.execute("select id from apidb WHERE id={0}".format(item['id']))
    if indb == 1: #if it is, update it
        try:
            q = 'UPDATE `apidb` SET `updated`="{0}", `members`={1}, \
            `category`={2}, `name`="{3}" WHERE `id`={4};\
            '.format(today,member.index(item['members']),
                     categorynames.index(item['type']),item['name'],item['id'])
            c.execute(q)
            db.commit()
        except Exception as e: #Errormessage out
            savelog('Update failed. Error: ' + str(e))
            return True
    else:
        return False

def save_picture(url,url2):
    id = url.split('gif?id=')[1] #getting the picture base filename
    small = "images/small/" + str(id) + '.png'
    large = "images/large/" + str(id) + '.png'
    if os.path.isfile(small) is False: #if the small file doesnt exist, save
        with request.urlopen(url) as response1, open(small, 'wb') as out_file:
            data1 = response1.read()
            out_file.write(data1)
            savelog('Small Image saved -> ' + str(id) + '.gif',False)
    if os.path.isfile(large) is False: #if the large file doesnt exists, save
        with request.urlopen(url2) as response2, open(large, 'wb') as out_file:
            data2 = response2.read()
            out_file.write(data2)
            savelog('Large Image saved -> ' + str(id) + '.gif',False)

def fetch(category, letter, page, sleep=True):
    if sleep == True:
        time.sleep(6)
    url = "http://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category="
    url += str(category) + "&alpha=" + str(letter) + "&page=" + str(page)
    try:
        query = json.loads(request.urlopen(url,timeout=30).read().decode('ISO-8859-1'))['items']
        if len(query) > 0:
            return query
        else:
            return None
    except Exception as e:
        print("Fetch failed: " + str(e))
        savelog(url)
        savelog(e)

def pager(category,letter,saveData=True,savePic=True):
    global categorynames
    stamp = date.today()
    today = stamp.strftime("%Y-%m-%d")

    if category == 0 and letter == '#':
        print("Category 0 is bugged at letter #. You have to add it manually.\n This message will keep posting until you add them.")
        return False

    for cat in [category] : #open the category
        for char in [letter]: #open the letter
            if char == '#':
                char = '%23'
            for page in list(range(1,50)): #page through
                savelog("--------------------")
                savelog("C: {0} L:'{1}' P: {2}".format(cat,char,page))
                savelog("--------------------")
                result = fetch(cat,char,page,False) #try to fetch the cat at letter

#                if result == False:
#                    savelog("<<< This query has been failed (no JSON returned) >>>")
#                    time.sleep(10)
#                    result = fetch(cat,char,page,False) #try to fetch the cat at letter
#                    if result == False:
#                        break
                while isinstance(result, list) == False: #Check the return type and keep resending the qury
                    time.sleep(10)
                    result = fetch(cat,char,page,False) #try to fetch the cat at letter
                    print("Query: {0}.".format(type(result)))
                    print('Resend Query..... Timeout 10s...')

                row = [] #stores item data for the database query

                for item in result:
                    if is_indb(item,today) == False:
                        #if an item has been found
                        #setting members value to true or false
                        if item['members'] == 'true':
                            item['members'] = int(1)
                        else:
                            item['members'] = int(0)
                        active = 1

                        #place into the list
                        row.append((item['id'],item['name'],item['description'],item['members'],cat,active,stamp,stamp))
                        savelog( "Added -> {0}".format(item['name']))
                    else:
                        savelog("Updated -> {0}".format(item['name']))
                    if savePic == True:
                        save_picture(item['icon'],item['icon_large'])
                if saveData == True: #write to the database
                    if len(row) > 0:
                        c.executemany('insert into apidb (id,name,description,members,category,active,updated,added) values (%s,%s,%s,%s,%s,%s,%s,%s)',row)
                        db.commit()
                if len(result) == 12:
                    savelog(">> Over next page")
                else:
                    savelog(">> Over next letter")
                    break

def savelog(log, verbose = True):
    with open('error.log', 'a') as f:
        f.write(log + '\n')
        f.close()
    if verbose:
        print(log)

def is_update_required():
    """Compare the remote DB to the local db"""
    category = list(range(0,42)) #iterateable category
    total = 0 #total number of remote items
    categoryDiff = [] #If a category doesnt match, stores them (category,alpha)
    print('-------------------')
    print('Checking Categories')
    print('-------------------')
    for i in category: #iterate trhough all category 0 - 41
        url = "http://services.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=" + str(i)
        try:
            alphabet = json.loads(request.urlopen(url, timeout=10)
                       .read())['alpha']
        except Exception as e:
            print("Error from is_update: " + e)

        subItemsPerCat = 0 #items in each catergory
        itemsPerCat = c.execute("select * from apidb where category="+str(i)+";")

        for letter in alphabet: #iterating through each letter in the cat.
            total += letter['items'] #all items
            subItemsPerCat += letter['items'] #cat subtotal

        if itemsPerCat != subItemsPerCat: #if remote doesnt match with local catsum
            print ('Difference in category {0}: {1}/{2}'.format(i,subItemsPerCat,itemsPerCat))
            alpha = ['#','a','b','c','d','e','f','g','h','i','j','k','l','m','n',\
                     'o','p','q','r','s','t','u','v','w','x','y','z']
            url = "https://secure.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=" + str(i)
            itemRemoteLetter = json.loads(request.urlopen(url, timeout=10)
                       .read())['alpha']

            letterCounter = -1 # this calls the nth item of itemRemoteLetter
            for letter in alpha: #iterating through each letter in the cat.
                letterCounter += 1
                if letter == '#': #special query witch regex
                    query = 'select id as num from apidb where category=' + str(i) + """ and name REGEXP "^([0-9]|[!@#\\$%\\^\\'\\&*\\)\\(+=._-])";"""
                    itemperLocalLetter = c.execute(query)
                else: #otherwise normal like query
                    query = 'select id as num from apidb where category=' + str(i) + ' and name like "{0}%";'.format(letter)
                    itemperLocalLetter = c.execute(query)

                print("Letter {0}. RemoteItems: {1}. LocalItems: {2}".format(letter,itemRemoteLetter[letterCounter]['items'],itemperLocalLetter))

                #if the sum/letter doesnt match
                if itemRemoteLetter[letterCounter]['items'] != itemperLocalLetter:
                    print("--------------------------------")
                    print("Difference found at letter '{0}'".format(letter))
                    print("--------------------------------")
                    pager(i,letter,True,False) #call the pager
        else: #if remote matches with local catsum
            print(" {0}   -> {1}/{2} ({3})".format(i,subItemsPerCat,itemsPerCat,categorynames[i]))

    totalLocalItems = c.execute("select * from apidb;")
    if total == totalLocalItems:
        savelog("Your database is up to date Remote: {0}, Local: {1}".format(total,totalLocalItems))
        return False
    else:
        savelog("Update required. Remote item: {0} - Local Item: {1}".format(total,totalLocalItems))
        return True

if __name__ == '__main__':
    try:
        print('Runescape Item Updater v1.0')
        savelog('---------------------------')
        savelog('Script Started at ' + str(datetime.now()))
        is_update_required()
        savelog('<<< Finished')
        db.close()
    except KeyboardInterrupt:
        savelog('---------------------------')
        savelog('<<< User aborted the script')
