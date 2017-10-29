from GetPlayers import AssignPoints, PrintPlayerList, GetPlayerListRating, GetPlayerListCost

#Globals TODO: Move them to a class so we dont need globals, this might get messy quickly
finalRating = 0
finalSelected = []

class Team:
	def __init__(self):
		pass

def main():
	players = AssignPoints(count=100)
	#PrintPlayerList(players)
	print knapsack_saveTeam_recursive(len(players)-1, 1000, players, [])
	#print basicDP(players, 1000)
	PrintPlayerList(finalSelected)

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

def basicDP(players, budget):
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


if __name__ == "__main__":
    main()