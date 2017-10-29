from GetPlayers import AssignPoints, PrintPlayerList, GetPlayerListRating, GetPlayerListCost

#Globals TODO: Move them to a class so we dont need globals, this might get messy quickly
finalRating = 0
finalSelected = []

class Team:
	def __init__(self):
		pass

def main():
	players = AssignPoints(count=6)
	#PrintPlayerList(players)
	print knapsack_saveTeam_recursive(len(players)-1, 1000, players, [])
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