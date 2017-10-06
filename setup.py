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
	data = ReadJsonFile(GetStatFileName())
	UpdateDB(data)
	AppendInfoToPlayers(data)


def main():
	# DownloadFile()
	# data = ReadJsonFile('FplData2017-09-22.json')
	# #AddToDB(data)
	# AppendInfoToPlayers(data)
	# GetMaxValues()
	# AssignPoints()
	# DownloadStatFile()
	SetupEnv()
	#AssignPoints()

if __name__ == "__main__":
    main()
