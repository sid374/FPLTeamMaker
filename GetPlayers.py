from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
import logging
import sys
import numpy
from sets import Set
import pdb
import thread
from repoze.lru import lru_cache

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

client = MongoClient('localhost', 27017)
db = client.fpl
playerCollection = db['playerInfo']

#
#
# Points and raking helper functions
#
#

class Player:
	def __init__(self):
		pass

	def __str__(self):
		return 'Name: ' + self.name + ' ' + self.position + ' Rating:' + str(self.rating) + '  Cost' + str(self.cost) + '; '
		#return 'Name: ' + self.name + ' Rating: ' + str(self.rating) + ' Cost: ' + str(self.cost)

	__repr__ = __str__

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

	
def GetPlayers(position, count = 6):
	maxValues = GetMaxValues()

	players = []
	for player in playerCollection.find({'position':position}).sort("total_points", DESCENDING):
		if count == 0:
			break
		count-=1
		rating = 0
		if player['position'] == 'FWD':
			rating = GetForwardRating(player, maxValues)
		elif player['position'] == 'MID':
			rating = GetMidRating(player, maxValues)
		elif player['position'] == 'DEF':
			rating = GetDefRating(player, maxValues)
		elif player['position'] == 'GKP':
			rating = GetDefRating(player, maxValues)
		p = Player()
		#p.rating = rating
		p.rating = player['total_points']
		p.cost = player['now_cost']
		p.name = player['first_name'] + player['second_name']
		p.team = player['teamName']
		p.id = player['id']
		p.position = player['position']
		players.append(p)

	players.sort(key = lambda x: x.rating, reverse = True)
	return players
	
def AssignPoints(count = 6):
	'''
	returns a list with count number of fwds, mids, defs and gks
	'''
	return GetPlayers('FWD', count) + GetPlayers('MID', count) + GetPlayers('DEF', count) + GetPlayers('GKP', count)

def PrintPlayerList(players):
	totalRating = 0
	totalCost = 0
	for p in players:
		print p
		totalCost += p.cost
		totalRating += p.rating
	print "Total rating = {0}, Total cost = {1}".format(totalRating, totalCost)

def AggregatePlayerList(players, fieldName):
	totalAggregate = 0
	for p in players:
		totalAggregate += getattr(p, fieldName)
	return totalAggregate
	
def GetPlayerListRating(players):
	return AggregatePlayerList(players, 'rating')

def GetPlayerListCost(players):
	return AggregatePlayerList(players, 'cost')

	#print selectedPlayers
	#ks, ksarr = KnapSackFPL(players, 1000, 20, 10)

	# ks, ksarr = KnapSackFPL(players = players[:20], budget = 1000, index = 20, selectedCount = 4)

	# tost = 0
	# rgs = 0
	# for p in ksarr:
	# 	print 'Name: ' + p.name + ' Rating: ' + str(p.rating) + ' Cost: ' + str(p.cost)
	# 	tost += p.cost
	# 	rgs += p.rating
	# print 'Total cost = ' + str(tost)
	# print 'Total rgs = ' + str(rgs)
	# print 'KS result = ' + str(ks)

	#print sorted(ratings, key=lambda x: x[0])

