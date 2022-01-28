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


    playCard(population, hand, e)

    sendHint(hintMoves)

def playCard(population, hand, e):
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
        if key["critical"]==1:
            losePoints = 6 - hand[key["card"]].value
            total = key["chance"]*2-(1-key["chance"])*e*(losePoints+1)
        else:
            total = key["chance"]-(1-key["chance"])*e
            total = key["critical"]*key["chance"] - (1-key["chance"])*e

    return
    
def sendHint(hintMoves):
    move = {
                "moveType":0,
                "hintType":0,
                "player":"",
                "value":0,
                "cards":0,    
                "critical":0
            }
    criticalSignal = 0
    bonusPoints = 0

    for m in hintMoves:
        a=0
         
    
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

