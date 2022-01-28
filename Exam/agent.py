from distutils.log import error
from functools import cache
from turtle import color
from numpy.random import choice
from Exam.moves import selectMoves
import GameData
import numpy as np
import moves

players=0
colors = ["red","white","blue","yellow","green"]
table = [0,0,0,0,0]
moveTypes = ["play","hint","discard"]
deckAvailableOthers = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")
population = []
hintMoves = []
hint = 0
errors = 0

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

            if hint.type == "value" and self.value==0:                            
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
                    isValue = np.sum(self.probs, axis=1)[0]            #checks if a value is found with exclusion
                    x = np.where(isValue == 1)
                    if x.size != 0:
                        self.value=x[0]+1
                    
                        
            elif hint.type == "color" and self.color == "":
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
                    isColor = np.sum(self.probs, axis=0)               #checks if a color is found with exclusion
                    y = np.where(isColor == 1)[0]
                    if y.size != 0:
                        self.value=colors[y[0]]
            
                    

class Player(object):  
    
    global hint
    global errors
    hand = []
    name = ""
    isMe = -1
    toServe = []
    deckAvailableSelf = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")
    teammates= {}
    

    states = np.array([   #row = value  column = color
        [2,2,2,2,2],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,1,1,1],
        [3,3,3,3,3]
    ], dtype="uint")

    global colors
    global table
    global deckAvailableOthers
    
    def __init__(self, cards, name, isMe) -> None:
        super().__init__()
        self.name = name
        self.isMe = isMe
        for _ in range(cards):
            self.hand.append(Card())
        
    
    def startgame(self, data):
        for key in data.players:
            name = key.name
            if name!=self.name:
                hand = []
                for c in key.hand:
                    hand.append((c.value, c.color, Card()))
                    self.deckAvailableSelf[c.value-1, colors.index(c.color)] -= 1
                self.teammates[name] = hand
                

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
        global hint
        global errors
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
            

            hint = data.usedNoteTokens
            errors = data.usedStormTokens
            count = len(self.toServe)
            for player in self.toServe:
                card = [p for p in data.players if p.name == player][0].hand[-1]
                #card = data.players['name'][player]['hand'][-1]
                self.deckAvailableSelf[card.value - 1, colors.index(card.color)] -= 1
                self.teammates[player][-1][0,1] = (card.value, card.color)
                self.newStates(card.value - 1, colors.index(card.color))
                self.toServe.pop(self.toServe.index(player))
            
            if(count > 0):
                
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
                self.deckAvailableOthers[data.card.value - 1, colors.index(data.card.color)] -=1
                self.newStates(data.card.value - 1, colors.index(data.card.color))
            else:
                self.toServe.append(data.lastPlayer)
                for i in range(self.hand):
                    if(self.teammates[data.lastPlayer][i][0,1] == (data.card.value, data.card.color)):
                        self.teammates[data.lastPlayer][i].pop()
                        self.teammates[data.lastPlayer][i].append((0,"", Card()))
        elif(type(data) is GameData.ServerHintData ):  ##hint has been given, update local cards
            if data.destination == self.name:
                for i in range(len(self.hand)):
                    self.hand[i].calcHint(data, i, self.deckAvailableSelf)                  #need to update all cards and available cards
            else:
                for i in range(len(self.hand)):
                    self.teammates[data.destination][i][2].calcHint(data, i, )
    
    def criticalHint(self):

        move = {
                "moveType":0,
                "hintType":0,
                "player":"",
                "value":0,
                "cards":0,    
                "critical":0
            }

        for key in self.teammates.keys():
            hand = self.teammates[key]
            for c in hand:
                if self.states[c[0]-1,c[1]] > 2:
                    move["moveType"] = "hint"
                    move["player"] = key
                    move["cards"] = 1
                    move["critical"] = 1

                    if c[2].value!=0:
                        move["hintType"] = "value" 
                        move["value"] = c[0]
                        
                    elif c[2].color!="":
                        move["hintType"] = "color"
                        move["value"] = c[1]
                        
                    

                    for hint in hintMoves:
                        if hint["player"] == move["player"] and hint["hintType"] == move["hintType"] and hint["value"] == move["value"]:
                            hint["cards"]+=1
                        else:
                            hintMoves.append(move)          
                    
        
        return

    def playableHint(self):
    
        move = {
                "moveType":0,
                "hintType":0,
                "player":"",
                "value":0,
                "cards":0,    
                "critical":0
            }

        for key in self.teammates.keys():
            hand = self.teammates[key]
            for c in hand:
                if self.states[c[0]-1,c[1]] == 2:
                    move["moveType"] = "hint"
                    move["player"] = key
                    move["cards"] = 1
                    move["critical"] = 0

                    if c[2].value!=0:
                        move["hintType"] = "value" 
                        move["value"] = c[0]
                        
                    elif c[2].color!="":
                        move["hintType"] = "color"
                        move["value"] = c[1]

                    for hint in hintMoves:
                        if hint["player"] == move["player"] and hint["hintType"] == move["hintType"] and hint["value"] == move["value"]:
                            hint["cards"]+=1
                        else:
                            hintMoves.append(move)          

        return

    def findMoves(self):
        global population
        move = {
                "card":0,
                "type":"",
                "critical":0,
                "chance":0,
            }

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

    def play():
        move = selectMoves(population, hintMoves, hint, errors)


    

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



