from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
import logging
import sys
import numpy
from sets import Set
import pdb
import thread
from functools import lru_cache

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
		return 'Name: ' + self.name + ' ' + self.position
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
	
def AssignPoints():
	return GetPlayers('FWD') + GetPlayers('MID') + GetPlayers('DEF') + GetPlayers('GKP')

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

cache = {}
iteration = 0
def KnapSackFPL(players, budget, index, selectedCount):
	#print budget
	global iteration
	global cache
	if budget in cache and index in cache[budget] and selectedCount in cache[budget][index]:
		print "Found in cache" + " Budget = " + str(budget) + " Index = " + str(index) + " Selected Count = " + str(selectedCount) + " Iteration = " + str(iteration)
		if len(cache[budget][index][selectedCount][1]) > 4:
			print cache[budget][index][selectedCount][1]
		return cache[budget][index][selectedCount]
	iteration += 1
	#print str(iteration)
	if index == 0 or budget == 0 or selectedCount == 0:
		return 0, []

	if players[index-1].cost > budget:
		return KnapSackFPL(players, budget, index-1, selectedCount)

	includeCurrent, includedArray = KnapSackFPL(players, budget-players[index-1].cost, index-1, selectedCount-1)
	excludeCurrent, excludedArray = KnapSackFPL(players, budget, index-1, selectedCount)

	includeCurrent += players[index-1].rating
	includedArray.append( players[index-1] )
	#print str(iteration)
	if(players[index-1].cost <= budget and includeCurrent > excludeCurrent):
		if budget not in cache:
			cache[budget] = {}
		if index not in cache[budget]:
			cache[budget][index] = {}
		cache[budget][index][selectedCount] = includeCurrent, includedArray
		return includeCurrent, includedArray
	else:
		if budget not in cache:
			cache[budget] = {}
		if index not in cache[budget]:
			cache[budget][index] = {}
		cache[budget][index][selectedCount] = excludeCurrent, excludedArray
		return excludeCurrent, excludedArray
'''
W: 9
Cost: 5 6 3 
Val : 9 1 2
'''
def KnapSack(costs, values, budget, index):
	if index == 0 or budget == 0:
		return 0, []

	if costs[index-1] > budget:
		return KnapSack(costs, values, budget, index-1)

	includeCurrent, includedArray = KnapSack(costs, values, budget-costs[index-1], index-1)
	excludeCurrent, excludedArray = KnapSack(costs, values, budget, index-1)

	includeCurrent += values[index-1] 
	includedArray.append(values[index-1])

	if(includeCurrent > excludeCurrent):
		return includeCurrent, includedArray
	else:
		return excludeCurrent, excludedArray

def KnapSackDP(costs, values, budget):
	dp = numpy.zeros((budget+1, len(costs)+1))

	for cost in range(budget+1):
		for i in range(len(costs)+1):
			if cost == 0 or i == 0:
				continue
			elif costs[i-1] <= cost:
				dp[cost][i] = max(values[i-1] + dp[cost-costs[i-1]][i-1], dp[cost][i-1])
			else:
				dp[cost][i] = dp[cost][i-1]

	selectedList = []
	row, col = budget, len(costs)
	while row >= 0 and col >= 0:
		if row-costs[col-1] >= 0 and dp[row][col] - values[col-1] == dp[row-costs[col-1]][col-1]:
			selectedList.append(values[col-1])
			row = row - costs[col-1]
			col = col-1
		else:
			col = col-1


	print dp
	print dp[budget][len(values)]
	print 'List' + str(selectedList)

	return dp[budget][len(values)]

def FPLKnapSackDP(players, budget):
	dp = numpy.zeros((budget+1, len(players)+1))

	for cost in range(budget+1):
		for i in range(len(players)+1):
			if cost == 0 or i == 0:
				continue
			elif players[i-1].cost <= cost:
				dp[cost][i] = max(players[i-1].rating + dp[cost-players[i-1].cost][i-1], dp[cost][i-1])
			else:
				dp[cost][i] = dp[cost][i-1]

	selectedList = []
	row, col = budget, len(players)
	while row >= 0 and col >= 0:
		if row-players[col-1].cost >= 0 and dp[row][col] - players[col-1].rating == dp[row-players[col-1].cost][col-1]:
			selectedList.append(players[col-1])
			row = row - players[col-1].cost
			col = col-1
		else:
			col = col-1

	return selectedList

fplCache = {}
	
def CacheHit(budget, index, formations):
	global fplCache
	if budget in fplCache and index in fplCache[budget] and str(formations) in fplCache[budget][index]:
		return True
	return False

def FPLKnapSack(players, budget, index, formations):
	global fplCache
	print "Budget = {}, index = {}, formations = {}".format(budget, index, formations)
	if budget == 0 or index == 0:
		return 0, []
		
	if CacheHit(budget, index, formations):
		return fplCache[budget][index][str(formations)]
		
	if players[index-1].cost > budget or formations[players[index-1].position] == 0:
		return FPLKnapSack(players, budget, index-1, formations)
		
	else:
		incFormations = formations.copy()
		incFormations[players[index-1].position] -= 1
		selectedVal, selectedArr = FPLKnapSack(players, budget-players[index-1].cost, index-1, incFormations)
		selectedVal += players[index-1].rating
		
		unselectedVal, unselectedArr = FPLKnapSack(players, budget, index-1, formations)

		if budget not in fplCache:
			fplCache[budget] = {}
		if index not in fplCache[budget]:
			fplCache[budget][index] = {}

		if selectedVal > unselectedVal:
			if len(selectedArr) == len(players):
				#pass
				print "Length = {0}".format(len(selectedArr)) + "Budget = {0}, index = {1}, formations = {2}".format(budget, index, formations)
				pdb.set_trace()
			selectedArr.append(players[index-1])
			fplCache[budget][index][str(formations)] = selectedVal, selectedArr
			return selectedVal, selectedArr
		else:
			fplCache[budget][index][str(formations)] = unselectedVal, unselectedArr
			return unselectedVal, unselectedArr


def Driver():
	players = AssignPoints()

	selectedPlayers = FPLKnapSackDP(players, 1000)
	print selectedPlayers

	totalCost = 0
	totalPoints = 0
	for p in selectedPlayers:
		totalCost += p.cost
		totalPoints += p.rating
		print "Name = {0}, Position = {1}".format(p.name, p.position)

	print "Total Cost = {0}".format(totalCost)
	print "Total Rating = {0}".format(totalPoints)

	print "Number of players = {0}".format(len(selectedPlayers))

def Driver2():
	players = AssignPoints()
	print players

	formations = {'GKP':1, 'DEF':0, 'MID':5, 'FWD':1}
	val, selectedPs = FPLKnapSack(players[:], 1000, 30, formations)
	#selectedPs.sort(key = lambda x: x.name)
	s = Set([(p.id, p.rating, p.name, p.position) for p in selectedPs])
	calculatedPoints = 0
	for p in sorted(s, key = lambda x: x[3]):
		print p
		calculatedPoints += p[1]
	print "Calculated points based on list = {0}".format(calculatedPoints)
	print "Returned points = {0}".format(val)
	print "Number of players = {0}".format(len(s))


def IsEmptyFormation(formations):
	for k,v in formations.iteritems():
		if v != 0:
			return False
			
	return True

def GetTeamRating(team):
	rating = 0
	for p in team:
		rating += p.rating
	return rating

bestTeamLock = thread.allocate_lock()
bestTeam = 0, []


@lru_cache(maxsize = None)
def KS(players, index, budget, selectedCount, selectedPlayers, formations):
	#print index, selectedCount
	global bestTeam
	
	if index == len(players) or budget == 0:
		return 0
		
	if IsEmptyFormation(formations) and selectedCount == 0:
		if GetTeamRating(selectedPlayers) > bestTeam[0]:
			#with a_lock:
			bestTeam = GetTeamRating(selectedPlayers), selectedPlayers
			print selectedPlayers
		return 0
		
	if players[index].cost > budget:
		KS(players, index+1, budget, selectedCount, selectedPlayers, formations)
	
	#thread.start_new_thread( KS, (players, index+1, budget, selectedCount, selectedPlayers, formations))
	excludeCurrent = KS(players, index+1, budget, selectedCount, selectedPlayers, formations)
	selectedPlayers.append(players[index])
	formations[players[index].position] -= 1
	#thread.start_new_thread( KS, (players, index+1, budget-players[index].cost, selectedCount - 1, selectedPlayers, formations))
	includeCurrent = KS(players, index+1, budget-players[index].cost, selectedCount - 1, selectedPlayers, formations)
	formations[players[index].position] += 1
	selectedPlayers.pop()
	
	return max(excludeCurrent, includeCurrent)
		

def Driver3():
	global bestTeam
	players = AssignPoints()
	selectedPlayers = []
	formations = {'GKP':2, 'DEF':5, 'MID':4, 'FWD':3}
	print KS(players, 0, 1000, 8, selectedPlayers, formations) 
	print bestTeam
	print KS.cache_info()


def main():
	Driver3()
	# costs = [1,2,3,4,5,6,7,8]
	# values = [5,3,4,41,5,67,8,2]
	# KnapSackDP(costs, values, 12)
	# value, valueArray =  KnapSack(costs, values, 9, len(costs))
	# print value 
	# print valueArray

if __name__ == "__main__":
    main()
