import requests
import time
import pickle
import pymongo
from pymongo import MongoClient
import os.path
import logging
import pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


JSON_FILE_NAME = 'FplData'
JSON_FILE_PATH = 'https://fantasy.premierleague.com/drf/bootstrap-static'

client = MongoClient('localhost', 27017)
db = client.fpl
playerCollection = db['playerInfo']


#
#
# DB and File Download Function
#
#

def GetStatFileName():
	'''
	Gets the file name appended with today's date
	'''
	timeStr = time.strftime("%Y-%m-%d")
	fileName = JSON_FILE_NAME + timeStr + '.json'
	return fileName


def DownloadStatFile():
	'''
	Downloads stat file from FPL. If the file has already been downloaded today, then it skips it.
	'''
	fileName = GetStatFileName()
	if os.path.isfile(fileName):
		logger.info("File already downloaded!") 
		return

	req = requests.get(JSON_FILE_PATH)

	if req.status_code != 200:
		logger.error("Download failed with code {0}".format(req.status_code))
	else:
		logger.debug("Stat file donwloaded succesfully with code {0}".format(req.status_code))

	jsonData = req.json()
	with open(fileName, 'w') as f:
		pickle.dump(jsonData, f)


def ReadJsonFile(fileName):
	'''
	Given a path to a pickled file, returns the content
	'''
	logger.debug("Reading Json File")
	with open(fileName, 'r') as f:
		data = pickle.load(f)
		return data

def AddToDB(dictData):
	'''
		Inserts a list of dictionary of players into the fpl['playerInfo'] collection
		dictData: Dictionary that contains key 'elements' which is a list of playerinfos from fpl
	'''
	playerCollection.create_index('id', unique = True)
	result = playerCollection.insert_many(dictData['elements'], ordered = False)
	if len(result) != len(dictData['elements']):
		logger.error("Failed to insert at least 1 entry")


def UpdateDB(dictData):
	'''
	Updates the db with new data, inserts data if it does not already exist.
	'''
	for player in dictData['elements']:
		doc = playerCollection.find_one_and_replace({'id' : player['id']}, player, upsert = True)
		if doc == None:
			logger.error('Could not update document with id: {0}'.format(player['id']))
		else:
			logger.debug('Updated {0} successfully'.format(player['id']))

def AppendInfoToPlayers(dictData):
	'''
	Appends position, teamName and teamcode to players already in the db. This is neccessary because of the structure of the json file
	dictData: Dictionary that contains key 'elements' which is a list of playerinfos from fpl
	'''

	#get data from file
	teamsDict = dict()
	elementTypesDict = dict()
	elementTypes = dictData['element_types']
	teams = dictData['teams']

	for t in teams:
		teamsDict[t['code']] = t

	for element in elementTypes:
		elementTypesDict[element['id']] = element

	for c in playerCollection.find():
		result = playerCollection.update_one(
			{'_id' : c['_id']},
			{'$set': {
				'position' : elementTypesDict[c['element_type']]['singular_name_short'],
				'teamName': teamsDict[c['team_code']]['short_name'],
				'teamDetails' : teamsDict[c['team_code']]
			}}, 
			upsert=False)
		if result.modified_count < 1:
			logger.error("Failed to append info to player {0}".format(c['id']))
	logger.debug('Successfulle appended info to players')


def SetupEnv():
	DownloadStatFile()
	data = ReadJsonFile('FplData2017-09-22.json')
	UpdateDB(data)
	AppendInfoToPlayers(data)


#
#
# Points and raking helper functions
#
#

def GetMaxValue(playerCollection, fieldToSortBy):
	for i in playerCollection.find().sort(fieldToSortBy, -1):
		return i[fieldToSortBy]

def GetMaxValues():
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
	# AssignPoints()
	# DownloadStatFile()
	SetupEnv()

if __name__ == "__main__":
    main()
