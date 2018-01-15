from GetPlayers import AssignPoints, PrintPlayerList, GetPlayerListRating, GetPlayerListCost, GetPlayers
import sys
import pickle

#Globals TODO: Move them to a class so we dont need globals, this might get messy quickly
finalRating = 0
finalSelected = []

class Team:
	def __init__(self):
		pass

def main():
	serializeList()
	deserializeList()
	#players = AssignPoints(count=10)
	#PrintPlayerList(players)
	#print knapsack_saveTeam_recursive(len(players)-1, 1000, players, [])
	cache = {}
	#print basicKnapsack_recursive_Cached(len(players)-1, 1000, players, cache)
	#print basicKnapsack_recursive(len(players)-1, 1000, players)
	#print ks_recursive_limit(len(players)-1, 1000, 3, players)
	#print basicDP(players, 1000)
	#PrintPlayerList(finalSelected)


def basicKnapsack_recursive(index, budget, players):
	'''
		Basic knapsack recursive algorithm
		index: integer last index of list
		budget: integer current budget
		players: list of players. object needs to have cost and rating properties
	'''
	if index < 0 or budget == 0:
		return 0
	if players[index].cost > budget:
		return basicKnapsack_recursive(index-1, budget, players)

	return max( 
				players[index].rating + basicKnapsack_recursive(index-1, budget-players[index].cost, players),
				basicKnapsack_recursive(index-1, budget, players )
			)


def basicKnapsack_recursive_Cached(index, budget, players, cache):
	'''
		Basic knapsack recursive algorithm
		index: integer last index of list
		budget: integer current budget
		players: list of players. object needs to have cost and rating properties
	'''
	if index < 0 or budget == 0:
		return 0
	try:
		if cache[index][budget]:
			return cache[index][budget]
	except KeyError as e:
		if index not in cache:
			cache[index] = {}
	if players[index].cost > budget:
		return basicKnapsack_recursive_Cached(index-1, budget, players, cache)
	retVal =  max( 
				players[index].rating + basicKnapsack_recursive_Cached(index-1, budget-players[index].cost, players, cache),
				basicKnapsack_recursive_Cached(index-1, budget, players, cache)
			)
	cache[index][budget] = retVal;
	return retVal


def knapsack_saveTeam_recursive(index, budget, players, selectedPlayers):
	'''
		Knapsack recursive algorith that keeps track of the selected players in global variables
		index: integer last index of list
		budget: integer current budget
		players: list of players. object needs to have cost and rating properties
		selectedPlayers: current selected players
	'''
	if index < 0 or budget == 0:
		global finalSelected
		global finalRating
		currentRating = GetPlayerListRating(selectedPlayers)
		if  currentRating > finalRating:
			finalSelected = selectedPlayers[:]
			finalRating = currentRating
		return 0
	if players[index].cost > budget:
		return knapsack_saveTeam_recursive(index-1, budget, players, selectedPlayers)

	unselectedRating = knapsack_saveTeam_recursive(index-1, budget, players, selectedPlayers)

	selectedPlayers.append(players[index])
	selectedRating = players[index].rating + knapsack_saveTeam_recursive(index-1, budget-players[index].cost, players, selectedPlayers)
	selectedPlayers.pop()

	return max(unselectedRating, selectedRating)


def basicDP(players, budget):
	'''
		Basic DP function for the knapsack problem. Does not take into further constraints and restrictions into account
	'''
	cache = [[0 for x in range(budget+1)] for x in range(len(players) + 1)]
	for player in xrange(len(players)+1):
		for cost in xrange(budget+1):
			if player == 0 or cost == 0:
				continue
			if players[player-1].cost > cost:
				#print cost
				cache[player][cost] = cache[player-1][cost]
			else:
				cache[player][cost] = max( players[player-1].rating + cache[player-1][cost-players[player-1].cost],
										 cache[player-1][cost] )

	#walk thorugh the cache to find the selected players
	selectedList = []
	player, cost = len(players), budget
	while player >= 0 and cost >= 0:
		if cost - players[player-1].cost > 0 and cache[player][cost] - players[player-1].rating == cache[player-1][cost - players[player-1].cost]:
			selectedList.append(players[player-1])
			cost = cost - players[player-1].cost
			player = player - 1	
		else:
			player = player - 1

	#Update global
	global finalSelected
	global finalRating
	finalSelected = selectedList[:]
	finalRating  = GetPlayerListRating(finalSelected)
	return cache[len(players)][budget]


def ks_recursive_limit(index, budget, playerCount, players):
	'''
		Basic recursive algorithm with an additional constraint of a max playerCount to be selected in the knapsack
	'''
	if index < 0 or budget == 0 or playerCount < 0:
		return 0
	if players[index].cost > budget:
		return ks_recursive_limit(index-1, budget, playerCount, players)
	return max( ks_recursive_limit(index-1, budget, playerCount, players),
				players[index].rating + ks_recursive_limit(index-1, budget-players[index].cost, playerCount-1, players) 
			)

def serializeList():
	players = AssignPoints(count=10)
	out = open('playerList.pkl', 'wb')
	pickle.dump(players, out)
	out.close()
	#print players

def deserializeList():
	pkl_file = open('playerList.pkl', 'rb')
	players = pickle.load(pkl_file)
	print players
	pkl_file.close()

if __name__ == "__main__":
    main()