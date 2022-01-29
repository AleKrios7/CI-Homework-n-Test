import numpy as np
from numpy.random import choice

def mask(probs, deck):
        res2 = np.ma.make_mask(probs)
        res3 = np.ma.masked_array(deck, np.invert(res2), fill_value=0)
        return res3.filled()
        

def selectMoves(population, hintMoves, hint, errors, hand, states):

    p = (8-hint)/8
    #proporzionalità inversa su hint disponibili

    e = (5 + errors*7)/(5 - errors) 
    

    c = -1

    #bp - d(1-p)
        
    #while c==-1:
    #    c = choice([1,0], 1, p)


    population = playCard(population, hand, e, p)
    hintMoves = sendHint(hintMoves, p)

    sorted(population, key = lambda p: p["reward"], reverse = True)
    sorted(hintMoves, key = lambda p: p["reward"], reverse = True)

    availableMoves = population[0:3]
    availableHints = hintMoves[0:3]
    totalMoves = 0
    totalHints = 0
    probsMoves = []
    probsHints = []
    
    for key in availableMoves:
        totalMoves += key["reward"]

    for key in availableHints:
        totalHints += key["reward"]

    for key in availableMoves:
        probsMoves.append(key["reward"]/totalMoves)

    for key in availableHints:
        probsHints.append(key["reward"]/totalHints)


    move = np.random.choice(availableMoves, 3, probsMoves)
    move = np.random.choice(availableHints, 3, probsHints)
    
    
    return move

def playCard(population, hand, e, p):
    playprobs = np.array([   #row = value  column = color
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1]
    ], dtype="float")
    move = {
                "card":0,
                "type":"",
                "critical":0,
                "chance":0,
            }
    #bonuses and penalties
    points = 0
    errors = 0
    losePoints = 0

    for key in population:
        if key["type"] == "play":
            if key["critical"] == 1:
                losePoints = 6 - key["card"].value
                if key["value"] == 5:
                    total = key["chance"]*(1 + p*2)*2-(1-key["chance"])*e*(losePoints+1)
                else:
                    total = key["chance"]*2-(1-key["chance"])*e*(losePoints+1)
            else:
                if key["value"] == 5:
                    total = key["chance"]*(1+p*2)-(1-key["chance"])*e
                else:
                    total = key["chance"]-(1-key["chance"])*e
        else:
            if key["critical"] == 1:
                losePoints = 6 - hand[key["card"]].value
                total = key["chance"]*2*(1+2*p)-(1-key["chance"])*(losePoints+1)
            else:
                total = key["chance"]*(1+2*p)
        
        key["reward"] = total

    return population
    
def sendHint(hintMoves, p):
    
    move = {
            "type":"",
            "hintType":"",
            "player":"",
            "value":0,
            "cards":[],    
            "critical":[],
            "playable":[],
            "cardValue":[],
            "cardColor": []
            }
    criticalSignal = 0
    bonusPoints = 0

    for m in hintMoves:
        tot = 0
        pointsaved = 0
        aff = 1
        for i in range(len(m["cards"])):
            if m["critical"][i] == 1 and m["playable"][i] == 1:
                pointsaved += 6 - m["cardValue"] + 1 +2*p*(m["cardValue"] == 5)
                
            elif m["critical"][i] == 1:
                pointsaved += 6 - m["cardValue"]
            else:
                pointsaved += 1 +2*p*(m["cardValue"] == 5)
        tot += aff * pointsaved - 2*p
        m["reward"] = tot
    return hintMoves        
        

         
    
    return
                                                                                       #according to my information
        #discard commands
        #type(data) is GameData.ServerActionValid #discard
        #type(data) is GameData.ServerActionInvalid #wrong command

        ##play commands
        #type(data) is GameData.ServerPlayerMoveOk #correct play
        #type(data) is GameData.ServerPlayerThunderStrike #wrong move

        ##error msg
        #type(data) is GameData.ServerInvalidDataReceived #invalid data

        ##game setup commands
        #type(data) is GameData.ServerGameOver #game over
        #type(data) is GameData.ServerPlayerStartRequestAccepted #start request (queue)
        #type(data) is GameData.ServerStartGameData #ready

        #for i in range(len(self.hand)):
        #   self.hand[i].calcProb(data, self.deckAvailableSelf)
        #devo decidere che update fare

