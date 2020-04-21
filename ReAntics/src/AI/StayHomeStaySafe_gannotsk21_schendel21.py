import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Stay Home Stay Safe")
        self.states = {}
        self.previousStates = 0 #[]
        self.alpha = .1
        self.discount = .7
        # e = probability that we're gonna choose a random state (0-100)
        self.eDecay = 0.9999
        self.e = 100
        self.eMin = 10

        self.fname = "gannotsk21_schendel21_states.txt"
        self.loadStateSpace('../'+self.fname)
        print(len(self.states))

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)]

        #Idea for explore Vs exploit
        # choosing next better state
        if random.randint(0, 100) > self.e:
            # choose based on the saved utilities
            for move in moves:
                if self.states.get(self.categorizeState(getNextStateAdversarial(currentState, selectedMove))) == None:
                    continue
                elif self.states.get(self.categorizeState(getNextStateAdversarial(currentState, move))) == None:
                    continue
                elif self.states[self.categorizeState(getNextStateAdversarial(currentState, selectedMove))] <self.states[self.categorizeState(getNextStateAdversarial(currentState, move))]:
                    selectedMove = move
        if self.e > self.eMin:
            self.e *= self.eDecay

        # #don't do a build move if there are already 3+ ants
        # numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        # while (selectedMove.moveType == BUILD and numAnts >= 5):
        #     selectedMove = moves[random.randint(0,len(moves) - 1)];

        # get next state
        nextState = getNextStateAdversarial(currentState, selectedMove)
        # current state is now the previous state
        self.previousStates = currentState
        # do calculations, pass 0 to show it's not a terminal state
        self.calculations(nextState, 0)
        # print(selectedMove.moveType)
        return selectedMove

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        reward = -1
        if hasWon:
            reward = 1
        self.calculations(self.previousStates, reward)
        self.saveStateSpace(self.fname)

    def saveStateSpace(self, path):
        f = open(path, "w")
        f.write("".join("{}: {}, ".format(k, v) for k, v in self.states.items()))
        f.close()

    def loadStateSpace(self, path):
        f = open(path, "r")
        self.states = {}
        dictionary = f.read()
        for entry in dictionary.split(', ')[0:-1]:
            pair = entry.split(': ')
            state = pair[0]
            weight = pair[1]
            self.states[state] = float(weight)
        f.close()

    ##
    #calculations
    #Description: calculates the utility of each states
    #
    #Parameters:
    #   nextState: next state after move is implemented
    #   hasWon: variable representing if state is a terminal state or not
    ##
    def calculations(self, nextState, hasWon):
        # getting reward for each state
        if hasWon == 0:
            reward = -.01
        else:
            reward = hasWon

        #look up utility in dictionary
        category = self.categorizeState(self.previousStates)
        utility = self.states.setdefault(category, 0)
        nextStateUtility = self.states.setdefault(self.categorizeState(nextState), 0)

        #Equation that I'm following => U(s)=U(s)+α⋅[R(s)+γ⋅U(s')−U(s)]
        TDequation = utility + self.alpha * (reward+(self.discount * (nextStateUtility - utility)))

        # checking variables
        # print("utility = " + str(utility))
        # print("nextStateUtility = " + str(nextStateUtility))
        # print("reward = " ,(reward))
        # print("TDequation = " + str(TDequation))

        #save into dictionary
        self.states[category] = TDequation


    ##
    #categorizeState
    #Description: returns the state in a string representing categories
    #
    #Parameters:
    #   currentState - The current state (GameState)
    ##
    def categorizeState(self, currentState):
        me = currentState.whoseTurn
        enemy = abs(me - 1)
        myInv = getCurrPlayerInventory(currentState)
        myFood = myInv.foodCount
        enemyInv = getEnemyInv(self, currentState)
        enemyFood = enemyInv.foodCount
        tunnels = getConstrList(currentState, types=(TUNNEL,))
        myTunnel = tunnels[1] if (tunnels[0].coords[1] > 5) else tunnels[0]
        enemyTunnel = tunnels[0] if (myTunnel is tunnels[1]) else tunnels[1]
        hills = getConstrList(currentState, types=(ANTHILL,))
        myHill = hills[1] if (hills[0].coords[1] > 5) else hills[0]
        enemyHill = hills[1] if (myHill is hills[0]) else hills[0]
        myQueen = myInv.getQueen()
        enemyQueen = enemyInv.getQueen()

        foods = getConstrList(currentState, None, (FOOD,))

        myWorkers = getAntList(currentState, me, (WORKER,))
        myOffense = getAntList(currentState, me, (SOLDIER, DRONE))
        enemyWorkers = getAntList(currentState, enemy, (WORKER,))
        enemyOffense = getAntList(currentState, enemy, (SOLDIER, DRONE, R_SOLDIER))

        score = ""
        score += str(myFood)#0: food count
        score += ";"
        score += str(myQueen.health)#1: queen health
        score += ";"
        score += str(myHill.captureHealth)#2: anthill health
        score += ";"
        score += str(len(myWorkers))#4: num of workers
        score += ";"
        #3: utility of worker to target
        tempScore = 0
        if len(myWorkers) > 0:
            for worker in myWorkers:
                if worker.carrying: # if carrying go to hill/tunnel
                    tempScore += 2
                    distanceToTunnel = approxDist(worker.coords, myTunnel.coords)
                    distanceToHill = approxDist(worker.coords, myHill.coords)
                    dist = min(distanceToHill, distanceToTunnel)
                    if dist <= 3:
                        tempScore += 1
                else: # if not carrying go to food
                    dist = 100
                    for food in foods:
                        temp = approxDist(worker.coords, food.coords)
                    if temp < dist:
                        dist = temp
                    if dist <= 3:
                        tempScore += 1
            score += str(tempScore)
        else:
            score += "0"
        score += ";"
        #5: average distance from our offense to enemy queen
        #6: average distance from our offense to the first enemy worker
        #7: average distance from our offense to enemy anthill
        queenDist = 0
        workerDist = 0
        anthillDist = 0
        if len(myOffense) > 0:
            for ant in myOffense:
                if enemyQueen is not None:
                    queenDist += approxDist(ant.coords, enemyQueen.coords)
                if len(enemyWorkers) > 0:
                    workerDist += approxDist(ant.coords, enemyWorkers[0].coords)
            anthillDist += approxDist(ant.coords, enemyHill.coords)
            score += str(queenDist//len(myOffense))
            score += ";"
            score += str(workerDist//len(myOffense))
            score += ";"
            score += str(anthillDist//len(myOffense))
            score += ";"
        else:
            score += "0;0;0;"
        #8: average distance from enemy offense to our queen
        #9: average distance from enemy offense to our anthill
        queenDist = 0
        anthillDist = 0
        if len(enemyOffense) > 0:
            for ant in enemyOffense:
                if myQueen is not None:
                    queenDist += approxDist(ant.coords, myQueen.coords)
                anthillDist += approxDist(ant.coords, myHill.coords)
            score += str(queenDist//len(enemyOffense))
            score += ";"
            score += str(anthillDist//len(enemyOffense))
        else:
            score += "0;0"

        return score