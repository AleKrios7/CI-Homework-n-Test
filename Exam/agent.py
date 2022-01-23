from functools import cache
from turtle import color
import GameData
import numpy as np

players=0
colors = ["red","white","blue","yellow","green"]
table = [0,0,0,0,0]
moveTypes = ["play","hint","discard"]
deckAvailableOthers = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")
population = []

class Card(object):
        def __init__(self) -> None:
            super().__init__()
        
        global colors

        value = 0
        color = ""
        probs = np.array([   #row = value  column = color
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1]
        ], dtype="float")

        def mask(self, probs, deck):
                res2 = np.ma.make_mask(probs)
                res3 = np.ma.masked_array(deck, np.invert(res2), fill_value=0)
                return res3.filled()
        
        def calcProb(self, deck):
            #calcolo probabilità cambiamento del deck (play/discard)

            #currentplayer
            #players = {name, hand=[carte in mano card={value,color}]} 
            #tablecards[color] = [card list of played cards]
            #discardPile = [card list of discarded cards] 
            #usedNoteToken = numero di hint dati 0-8
            #usedStormTokens = numero di errori 0-2 (a 3 la partita finisce)
            tot = 0
            m = self.mask(self.probs, deck)
            tot = np.sum(m)
            self.probs = m/tot
        
        def calcHint(self, hint, mypos, deck):

            #calcolo probabilità ricezione indizi (hint)
            #hint.type             value o color (type)
            #hint.destination      player to
            #hint.value            number or string (effective value)
            #hint.positions        array delle posizioni

            if hint.type == "value":                            
                if mypos in hint.positions:
                    self.value = hint.value
                    for i in range(5):
                        if(i != hint.value-1):
                            self.probs[i].fill(0)
                    m = self.mask(self.probs, deck)
                    tot = np.sum(m[hint.value-1])
                    self.probs[hint.value-1,:] = m[hint.value-1,:]/tot
                else:
                    self.probs[hint.value-1].fill(0)
                    tot = 0
                    m = self.mask(self.probs, deck)
                    tot = np.sum(m)
                    self.probs = m/tot
            elif hint.type == "color":
                if mypos in hint.positions:                             #if the card is the target is the card being processed
                    self.color = hint.value                             #update color of card (known)
                    for i in range(5):
                        if colors[i]!=hint.value:                       #other colors are not possible
                            self.probs[:,i]=0                           #remove probabilities
                        else:
                            x=i
                        m = self.mask(self.probs, deck)
                    tot = np.sum(m[:, x])
                    self.probs[:, x] = m[:, x]/tot            #update probabilities
                else:
                    i = colors.index(hint.value)
                    self.probs[:,i] = 0
                    tot = 0
                    m = self.mask(self.probs, deck)
                    tot = np.sum(m)
                    self.probs = m/tot
                    

class Player(object):  
    hand = []
    name = ""
    isMe = -1
    toServe = []
    deckAvailableSelf = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")
    teammates= []

    states = np.array([   #row = value  column = color
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0]
    ], dtype="uint")
    
    global colors
    global table
    #global deckAvailableOthers
    
    def __init__(self, cards, name, isMe, numPlayers) -> None:
        super().__init__()
        self.name = name
        self.isMe = isMe
        for _ in range(cards):
            self.hand.append(Card())
        
    
    def startgame(self, data):
        for key in data.players:
            for card in key.hand:
                self.deckAvailableSelf[card.value-1, colors.index(card.color)] -= 1

    def play(index):
        print("To implement")

    def discard(index):
        print("To implement")
    
    def move():
        veryintelligentmove = "show"
        return veryintelligentmove
    
    def newStates(self, i, j):
        if(self.deckAvailableSelf[i,j] != 0):
            if i+1<=table[j]:
                crit = False
            else :
                crit = self.deckAvailableSelf[i][j]==1
                play = (i == table[j])
                if(not crit and not play): #discardable
                    self.states[i,j] = 1
                elif(crit and not play):   #critical no playable
                    self.states[i,j] = 3
                elif(play and not crit):   #playable not critical
                    self.states[i,j] = 2
                else:
                    self.states[i,j] = 4   #playable and critical
        else:
            self.states[i,j] = 0           #not in game anymore :(
                
    
    def update(self, data):  #entra qui se ricevo hint o se qualcuno/io gioco/scarto
                             #aggiorna saved decks
        if(type(data) is GameData.ServerGameStateData):                         
            ##show has been called, update is needed
            #TODO: modifica deck values using data
            #change single hand cards probabilities

            #currentplayer
            #players = [{name, hand=[carte in mano card={value,color}]}]
            #tablecards[color] = [card list of played cards]
            #discardPile = [card list of discarded cards] 
            #usedNoteToken = numero di hint dati 0-8
            #usedStormTokens = numero di errori 0-2 (a 3 la partita finisce)
            

            count = len(self.toServe)
            for player in self.toServe:
                card = [p for p in data.players if p.name == player][0].hand[-1]
                #card = data.players['name'][player]['hand'][-1]
                self.deckAvailableSelf[card.value - 1, colors.index(card.color)] -= 1
                self.newStates(card.value - 1, colors.index(card.color))
                self.toServe.pop(self.toServe.index(player))
            
            if(count > 0):
                self.teammates=[]
                for player in data.players:
                    self.teammates.append(player.hand)
                for i in range(len(self.hand)):
                    self.hand[i].calcProb(self.deckAvailableSelf)
                for t in data.tableCards.keys():
                    if len(data.tableCards[t]):
                        table[colors.index(t)] = data.tableCards[t][-1].value
            
            

        elif(type(data) is GameData.ServerActionValid 
            or type(data) is GameData.ServerPlayerThunderStrike
            or type(data) is GameData.ServerPlayerMoveOk):
            #action -> string di contenuto "discard"
            #card -> {color, value}
            #lastplayer -> string giocatore che ha giocato
            #player -> giocatore che deve giocare
            if(data.lastPlayer == self.name):
                self.deckAvailableSelf[data.card.value - 1, colors.index(data.card.color)] -= 1
                self.newStates(data.card.value - 1, colors.index(data.card.color))
            else:
                self.toServe.append(data.lastPlayer)


        elif(type(data) is GameData.ServerHintData and data.destination == self.name):  ##hint has been given, update local cards
            for i in range(len(self.hand)):
                self.hand[i].calcHint(data, i, self.deckAvailableSelf)                  #need to update all cards and available cards


    def findMoves(self):
        global population

        for card in self.hand:
            if card.value!=0 and card.color!="":

                if self.states[card.value-1, colors.index(card.color)]==2 or self.states[card.value-1, colors.index(card.color)]==4:
                    move["card"]=self.hand.index(card)
                    move["type"]="play"
                    move["chance"]=1
                    move["critical"]= self.states[card.value-1, colors.index(card.color)]==4
                    population.append(move)
                elif self.states[card.value-1, colors.index(card.color)]==1:
                    move["card"]=self.hand.index(card)
                    move["type"]="discard"
                    move["chance"]=1
                    population.append(move)
            elif card.value!=0 and card.color=="":
                cardTmp = card
                for color in colors:
                    cardTmp.color=color
                    if self.states[cardTmp.value-1, colors.index(cardTmp.color)]==2 or self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4:
                        move["card"] = self.hand.index(card)
                        move["type"] = "play"
                        move["chance"] = card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["critical"] = self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4
                        population.append(move)
                    elif self.states[cardTmp.value-1, colors.index(cardTmp.color)]==1:
                        move["card"]=self.hand.index(card)
                        move["type"]="discard"
                        move["chance"]=card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        population.append(move)
            elif card.value==0 and card.color!="":
                cardTmp = card
                for i in range(5):
                    cardTmp.value=i
                    if self.states[cardTmp.value-1, colors.index(cardTmp.color)]==2 or self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4:
                        move["card"] = self.hand.index(card)
                        move["type"] = "play"
                        move["chance"] = card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["critical"] = self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4
                        population.append(move)
                    elif self.states[card.value-1, colors.index(cardTmp.color)]==1:
                        move["card"]=self.hand.index(card)
                        move["type"]="discard"
                        move["chance"]=card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        population.append(move)
            elif card.value==0 and card.color=="" and card.probs.min() == 0:
                m = card.mask(card.probs, self.states)
                cardTmp = card
                for i in range(5):
                    cardTmp.value=i
                    if m[cardTmp.value-1, colors.index(cardTmp.color)]==2 or m[cardTmp.value-1, colors.index(cardTmp.color)]==4:
                        move["card"] = self.hand.index(card)
                        move["type"] = "play"
                        move["chance"] = card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["critical"] = m[cardTmp.value-1, colors.index(cardTmp.color)]==4
                        population.append(move)
                    elif m[card.value-1, colors.index(cardTmp.color)]==1:
                        move["card"]=self.hand.index(card)
                        move["type"]="discard"
                        move["chance"]=card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        population.append(move)
                


                return

            move = {
                "card":0,
                "type":"",
                "critical":0,
                "chance":0,
            }
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


def isCritical(card, deck):
    global colors
    global table
    if card.value<=table[colors.index(card.color)]:
        return False
    return deck[card.value -1][colors.index(card.color)]==1

def isDiscardable(card, deck):
    return not (isCritical(card, deck) or isPlayable(card))

def isPlayable(card):
    global colors
    global table
    return card.value == table[colors.index(card.color)]+1



