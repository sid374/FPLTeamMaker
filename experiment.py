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
	#dp = numpy.zeros((budget+1, len(costs)+1))
	dp = [[{'val': 0, 'count':0} for x in range(len(costs)+1)] for y in range(budget+1)]
	for cost in range(budget+1):
		for i in range(len(costs)+1):
			if cost == 0 or i == 0:
				continue
			elif costs[i-1] <= cost:
				pdb.set_trace()
				selectCurrent = values[i-1] + dp[cost-costs[i-1]][i-1]['val']
				excludeCurrent = dp[cost][i-1]['val']
				if selectCurrent > excludeCurrent:
					dp[cost][i]['val'] = selectCurrent
					dp[cost][i]['count'] = dp[cost-costs[i-1]][i-1]['count'] + 1
				else:
					dp[cost][i]['val'] = excludeCurrent
					dp[cost][i]['count'] = dp[cost][i-1]['count']
			else:
				dp[cost][i]['val'] = dp[cost][i-1]
				dp[cost][i]['count'] = dp[cost][i-1]['count']

	selectedList = []
	row, col = budget, len(costs)
	while row >= 0 and col >= 0:
		if row-costs[col-1] >= 0 and dp[row][col]['val'] - values[col-1] == dp[row-costs[col-1]][col-1]['val']:
			selectedList.append(values[col-1])
			row = row - costs[col-1]
			col = col-1
		else:
			col = col-1


	for row in dp:
		print row
	print dp[budget][len(values)]['val']
	print 'List' + str(selectedList)

	return dp[budget][len(values)]['val']

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
bestTeam = [0, []]
count = 0

#@lru_cache(2 = None)
def KS(players, index, budget, selectedPlayers, formations):
	#print index, selectedCount
	global count
	global bestTeam

	#print count
	count += 1
	
	if IsEmptyFormation(formations):
		teamRating = GetTeamRating(selectedPlayers)
		if teamRating > bestTeam[0]:
			#with a_lock:
			bestTeam[0] = teamRating
			bestTeam[1] = selectedPlayers
			print bestTeam[1]
			print teamRating
		return teamRating

	if index == len(players) or budget <= 0:
		return 0
		
	if players[index].cost > budget:
		return KS(players, index+1, budget, selectedPlayers, formations)
	
	#thread.start_new_thread( KS, (players, index+1, budget, selectedCount, selectedPlayers, formations))
	excludeCurrent = KS(players, index+1, budget, selectedPlayers, formations)
	selectedPlayers.append(players[index])
	formations[players[index].position] -= 1
	#thread.start_new_thread( KS, (players, index+1, budget-players[index].cost, selectedCount - 1, selectedPlayers, formations))
	includeCurrent = KS(players, index+1, budget-players[index].cost, selectedPlayers, formations) + players[index].rating
	formations[players[index].position] += 1
	selectedPlayers.pop()
	#print "Exclude {0} Include {1} index = {2} BestTeam = {3}".format(excludeCurrent, includeCurrent, index, bestTeam) 
	return max(excludeCurrent, includeCurrent)
		
best = 0,[]
def KS2(players, index, budget, selectedPlayers, selectedCount):
	global best
	if selectedCount == 0:
		global best
		print best
		if GetTeamRating(selectedPlayers) > best[0]:
			best = GetTeamRating(selectedPlayers), selectedPlayers
			print best[0]
		return 0
	if budget == 0 or index == 0:
		#print selectedPlayers
		return 0

	if players[index].cost > budget:
		return KS2(players, index-1, budget, selectedPlayers, selectedCount)

	excludeCurrent = KS2(players, index-1, budget, selectedPlayers, selectedCount)

	selectedPlayers.append(players[index])
	includeCurrent = players[index].rating + KS2(players, index-1, budget - players[index].cost, selectedPlayers, selectedCount - 1)
	selectedPlayers.pop()

	return max(includeCurrent, excludeCurrent)

def Driver3():
	global bestTeam
	players = AssignPoints(count = 10)
	for p in players:
		print "{0} {1} {2}".format(p, p.rating, p.cost)
	print GetTeamRating(players)
	selectedPlayers = []
	formations = {'GKP':2, 'DEF':5, 'MID':3, 'FWD':3}
	print KS(players, 0, 1000, selectedPlayers, formations)
	print bestTeam
	print selectedPlayers
	#print KS.cache_info()

def Driver4():
	global best
	players = AssignPoints(count = 2)
	for p in players:
		print "{0} {1} {2}".format(p, p.rating, p.cost)
	print GetTeamRating(players)
	selectedPlayers = []
	print KS2(players, len(players)-1, 1000, selectedPlayers, 3)
	print best
def main():
	#Driver4()
	Driver3()
	# costs = [1,2,3,1,2,3]
	# values = [5,3,8,1,2,3]
	# KnapSackDP(costs, values, 6)
	# value, valueArray =  KnapSack(costs, values, 9, len(costs))
	# print value 
	# print valueArray

if __name__ == "__main__":
    main()
