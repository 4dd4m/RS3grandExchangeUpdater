from urllib import request
from datetime import datetime
import pickle, os, pprint, time, json, sqlite3
import pymysql

db = pymysql.connect('localhost','root','root','flip',autocommit=True)
c = db.cursor()


categorynames = ["Miscellaneous",
					"Ammo",
					"Arrows",
					"Bolts",
					"Construction materials",
					"Construction projects",
					"Cooking ingredients",
					"Costumes",
					"Crafting materials",
					"Familiars",
					"Farming produce",
					"Fletching materials",
					"Food and drink",
					"Herblore materials",
					"Hunting equipment",
					"Hunting Produce",
					"Jewellery",
					"Mage armour",
					"Mage weapons",
					"Melee armour - low level",
					"Melee armour - mid level",
					"Melee armour - high level",
					"Melee weapons - low level",
					"Melee weapons - mid level",
					"Melee weapons - high level",
					"Mining and Smithing",
					"Potions",
					"Prayer armour",
					"Prayer materials",
					"Range armour",
					"Range weapons",
					"Runecrafting",
					"Runes, Spells and Teleports",
					"Seeds",
					"Summoning scrolls",
					"Tools and containers",
					"Woodcutting product",
					"Pocket items",
					"Construction products",
					"Food and Drink"
				]

def is_indb(item):
	if item['members'] == 'true':
		item['members'] = 1;
	else:
		item['members'] = 0;
	indb = c.execute("select id from apidb WHERE id={0}".format(item['id']))
	if indb == 1:
		try:
			q = 'UPDATE `apidb` SET `updated`={0}, `members`={1}, `category`={2}, `name`="{3}" WHERE `id`={4};'.format(int(time.time()),item['members'],categorynames.index(item['type']),item['name'],item['id'])
			c.execute(q)
			db.commit()
		except Exception as e:
			savelog('Update failed. Error: ' + str(e))
		return True
	else:
		return False

def save_picture(url,url2):
	path = "C:\\Users\\Adam\\Desktop\\UwAmp\\www\\fliplog\\images\\"
	id = url.split('gif?id=')[1]
	small = path + "small\\" + str(id) + '.png'
	large = path + "large\\" + str(id) + '.png'
	if os.path.isfile(small) is False:
		with request.urlopen(url) as response1, open(small, 'wb') as out_file:
			data1 = response1.read()
			out_file.write(data1)
			savelog('Small Image saved -> ' + str(id) + '.gif')
	if os.path.isfile(large) is False:    
		with request.urlopen(url2) as response2, open(large, 'wb') as out_file:
			data2 = response2.read()
			out_file.write(data2)
			savelog('Large Image saved -> ' + str(id) + '.gif')

def fetch(category, letter, page, sleep=True):
    if sleep == True:
        time.sleep(7)
    url = "http://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category="
    url += str(category)
    url += "&alpha="+ str(letter)
    url += "&page=" + str(page)
    try:
        query = json.loads(request.urlopen(url,timeout=30).read().decode('ISO-8859-1'))['items']
        if len(query) > 0:
            return query
        else:
            return None
    except Exception as e:
        savelog(url)
        savelog(e)


def first(catarg=32,charinit='g',saveData=True,savePic=True):
	global categorynames
	empty_pages = [] 
	firstrun = True
	category = list(range(catarg,38))
	fullalphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','%23']


	for cat in category :
		if firstrun == False:
			letter = fullalphabet
		else:
			letter = fullalphabet[fullalphabet.index(charinit):]
            
		for char in letter:
    
			for page in list(range(1,10)):
				if firstrun == True:
					result = fetch(cat,char,page,False)
					firstrun = False
				else:
					result = fetch(cat,char,page)
				if result == None:
					numOfResult = 0
				else:
					try:
						numOfResult = len(result)
					except Exception as e:
						return e
				savelog("------------------------------------------------------------")
				savelog("Categroy: {0}. Letter: {1}. Page: {2}. Returned items: {3}".format(cat,char,page,numOfResult))
				savelog("------------------------------------------------------------")

				if result == None:
					savelog("<<< This Letter contains no Items >>>")
					empty_pages += {'letter' : char, 'page' : page, 'category' : cat}
					break
				row = [] 

				for item in result:
					
					if is_indb(item) == False:
						#if an item has been found
						#setting members value to true or false
						if item['members'] == 'true':
							item['members'] = int(1)
						else:
							item['members'] = int(0)
						active = 1

						#place into the list
						row.append((item['id'],item['name'],item['description'],item['members'],cat,active,time.time()))
						savelog( "Added -> {0}".format(item['name']))
					else:
						savelog("Updated -> {0}".format(item['name']))
					if savePic == True:
						save_picture(item['icon'],item['icon_large'])
				if saveData == True: #write to the database
					if len(row) > 0:
						c.executemany('insert into apidb (id,name,description,members,category,active,updated) values (%s,%s,%s,%s,%s,%s,%s)', row)
						db.commit()
				if len(result) < 12:
					savelog(">> Over next letter")
					break

def savelog(log, verbose = True):
	with open('error.log', 'a') as f:
		f.write(log + '\n')
		f.close()
	if verbose:
		print(log)

def is_update_required():

    category = list(range(0,31))
    total = 0
    for i in category:
        print("5 {0}".format(i))
#        time.sleep(7)
        url = "http://services.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=" + str(i)
        response = json.loads(request.urlopen(url, timeout=10).read())
        for letter in response['alpha']:
            total += letter['items']

    print("Found {0} items...".format(total))
    dbresult = c.execute("select count(*) from apidb")
    local = int(dbresult.fetchone()[0])
    print("Collecting local items.... {0}".format(local))
    if total == local:
        savelog("Your database is up to date")
        return False
    else:
        savelog("Update required")
        return True

if __name__ == '__main__':
	try:
		print('Runescape Item Updater v1.0')
		savelog('---------------------------')
		savelog('Script Started at ' + str(datetime.now()))

		first()
		savelog('<<< Finished')
		db.close()
	except KeyboardInterrupt:
		savelog('---------------------------')
		savelog('<<< User aborted the script')
	except Exception as e:
		savelog('Error: ' + str(e))
