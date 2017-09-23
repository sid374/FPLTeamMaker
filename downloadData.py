import requests
import time
import pickle
import pymongo
from pymongo import MongoClient

def DownloadFile():
	r = requests.get('https://fantasy.premierleague.com/drf/bootstrap-static')
	jr = r.json()
	timeStr = time.strftime("%Y-%m-%d")
	with open('FplData'+timeStr+'.json', 'w') as f:
		pickle.dump(jr, f)

def ReadJsonFile(fileName):
	with open(fileName, 'r') as f:
		data = pickle.load(f)
		return data

def AddToDB(dictData):
	'''
		Inserts a list of dictionary of players into the fpl['playerInfo'] collection
		dictData: Dictionary that contains key 'elements' which is a list of playerinfos from fpl
	'''
	client = MongoClient('localhost', 27017)
	db = client.fpl
	playerCollection = db['playerInfo']
	playerCollection.insert_many(dictData['elements'])

def AppendInfoToPlayers(dictData):
	client = MongoClient('localhost', 27017)
	db = client.fpl
	playerCollection = db['playerInfo']

	#get data from file
	teamsDict = dict()
	elementTypesDict = dict()
	elementTypes = dictData['element_types']
	teams = dictData['teams']

	for t in teams:
		teamsDict[t['code']] = t

	for element in elementTypes:
		elementTypesDict[element['id']] = element

	print teamsDict

	for c in playerCollection.find():
		playerCollection.update(
			{'_id' : c['_id']},
			{'$set': {
				'position' : elementTypesDict[c['element_type']]['singular_name_short'],
				'teamName': teamsDict[c['team_code']]['short_name'],
				'teamDetails' : teamsDict[c['team_code']]
			}}, 
			upsert=False, multi=False)

def GetMaxValue(playerCollection, fieldToSortBy):
	for i in playerCollection.find().sort(fieldToSortBy, -1):
		return i[fieldToSortBy]

def GetMaxValues():
	client = MongoClient('localhost', 27017)
	db = client.fpl
	playerCollection = db['playerInfo']

	maxValues = dict()
	maxValues['goals_scored'] = GetMaxValue(playerCollection, 'goals_scored')
	maxValues['minutes'] = GetMaxValue(playerCollection, 'minutes')
	maxValues['assists'] = GetMaxValue(playerCollection, 'assists')
	maxValues['bonus'] = GetMaxValue(playerCollection, 'bonus')
	maxValues['clean_sheets'] = GetMaxValue(playerCollection, 'clean_sheets')


	return maxValues

def GetNormalizedRating(player, attribute, maxValues):
	if attribute not in player:
		return
	rating = player[attribute] * 100/ maxValues[attribute]
	#print  attribute + ' ' + str(rating)
	return rating

def GetForwardRating(player, maxValues):
	rating = 0
	rating = rating + GetNormalizedRating(player,'goals_scored', maxValues) * 4
	rating = rating + GetNormalizedRating(player,'minutes', maxValues) * 2
	rating = rating + GetNormalizedRating(player,'assists', maxValues) * 3
	rating = rating + GetNormalizedRating(player,'bonus', maxValues)  * 3
	return rating

def GetMidRating(player, maxValues):
	rating = 0
	rating = rating + GetNormalizedRating(player,'goals_scored', maxValues) * 5
	rating = rating + GetNormalizedRating(player,'minutes', maxValues) * 2
	rating = rating + GetNormalizedRating(player,'assists', maxValues) * 3
	rating = rating + GetNormalizedRating(player,'bonus', maxValues)  * 3
	rating = rating + GetNormalizedRating(player,'clean_sheets', maxValues)  * 1
	return rating

def GetDefRating(player, maxValues):
	rating = 0
	rating = rating + GetNormalizedRating(player,'goals_scored', maxValues) * 6
	rating = rating + GetNormalizedRating(player,'minutes', maxValues) * 2
	rating = rating + GetNormalizedRating(player,'assists', maxValues) * 3
	rating = rating + GetNormalizedRating(player,'bonus', maxValues)  * 3
	rating = rating + GetNormalizedRating(player,'clean_sheets', maxValues)  * 4
	return rating

def GetGKRating(player, maxValues):
	return GetDefRating(player, maxValues)

def AssignPoints():
	client = MongoClient('localhost', 27017)
	db = client.fpl
	playerCollection = db['playerInfo']

	maxValues = GetMaxValues()

	ratings = []
	for player in playerCollection.find():
		if player['position'] == 'FWD':
			rating = GetForwardRating(player, maxValues)
		elif player['position'] == 'MID':
			rating = GetMidRating(player, maxValues)
		elif player['position'] == 'DEF':
			rating = GetDefRating(player, maxValues)
			ratings.append((rating, player['second_name']))
		elif player['position'] == 'GK':
			rating = GetDefRating(player, maxValues)
			ratings.append((rating, player['second_name']))

	print sorted(ratings, key=lambda x: x[0])


def Temp():
	data = ReadJsonFile('FplData2017-09-22.json')
	for player in data['elements']:
		print player['first_name']


def main():
	# DownloadFile()
	# data = ReadJsonFile('FplData2017-09-22.json')
	# #AddToDB(data)
	# AppendInfoToPlayers(data)
	# GetMaxValues()
	AssignPoints()

if __name__ == "__main__":
    main()
