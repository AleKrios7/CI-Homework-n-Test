from moves import selectMoves
import GameData
import numpy as np
import copy 


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

        def copy(self):
            c = Card()
            c.value = self.value
            c.color = self.color
            c.probs = copy.deepcopy(self.probs)
            return c

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
                    for x in range(5):
                        if(x != hint.value-1):
                            self.probs[x, :]=0
                else:
                    self.probs[hint.value-1, :] = 0
                    self.calcProb(deck)
                    isValue = np.sum(self.probs, axis=1)[0]            #checks if a value is found with exclusion
                    x = np.where(isValue == 1)
                    if x[0].size != 0:
                        self.value=x[0]+1
                    
                        
            elif hint.type == "color" and self.color == "":
                if mypos in hint.positions:                             #if the card is the target is the card being processed
                    self.color = hint.value                             #update color of card (known)
                    for i in range(5):
                        if colors[i]!=hint.value:                       #other colors are not possible
                            self.probs[:,i]=0                           #remove probabilities
            #update probabilities
                else:
                    i = colors.index(hint.value)
                    self.probs[:,i]=0
                    self.calcProb(deck)
                    isColor = np.sum(self.probs, axis=0)               #checks if a color is found with exclusion
                    y = np.where(isColor == 1)[0]
                    if y.size != 0:
                        self.value=colors[y[0]]
                
            self.calcProb(deck)
            
                    

class Player(object):  
    
    global hint
    global errors
    hand = []
    name = ""
    isMe = -1
    first = 0
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
            newCard = Card()
            self.hand.append(newCard)
         
    def startgame(self, data):
        for key in data.players:
            name = key.name
            if name!=self.name:
                hand = []
                for c in key.hand:
                    newCard = Card()
                    self.deckAvailableSelf[c.value-1, colors.index(c.color)] -= 1
                    newCard.calcProb(self.deckAvailableSelf)
                    hand.append([c.value, c.color, copy.deepcopy(newCard)])
                self.teammates[name] = copy.deepcopy(hand)

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
        global deckAvailableOthers
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
                card = copy.deepcopy([p for p in data.players if p.name == player][0].hand[-1])
                #card = data.players['name'][player]['hand'][-1]
                self.deckAvailableSelf[card.value - 1, colors.index(card.color)] -= 1
                tuple = [card.value, card.color, copy.deepcopy(self.teammates[player][-1][2])]
                self.teammates[player].pop(-1)
                self.teammates[player].append(tuple)
                self.newStates(card.value - 1, colors.index(card.color))
                self.toServe.pop(self.toServe.index(player))
                
            
            if count > 0 or self.first==0:
                self.first=1
                for i in range(len(self.hand)):
                    self.hand[i].calcProb(self.deckAvailableSelf)
                #for t in data.tableCards.keys():
                #    if len(data.tableCards[t]):
                #        table[colors.index(t)] = data.tableCards[t][-1].value

                for key in data.players:
                    name = key.name
                    if name!=self.name:
                        hand = []
                        for c in key.hand:
                            newCard = Card()
                            
                            newCard.calcProb(deckAvailableOthers)
                            hand.append([c.value, c.color, copy.deepcopy(newCard)])
                        self.teammates[name] = copy.deepcopy(hand)

        elif(type(data) is GameData.ServerActionValid 
            or type(data) is GameData.ServerPlayerThunderStrike
            or type(data) is GameData.ServerPlayerMoveOk):
            #action -> string di contenuto "discard"
            #card -> {color, value}
            #lastplayer -> string giocatore che ha giocato
            #player -> giocatore che deve giocare
            if type(data) is GameData.ServerPlayerMoveOk:
                ##qui?
                table[colors.index(data.card.color)]= data.card.value


            if(data.lastPlayer == self.name):
                self.deckAvailableSelf[data.card.value - 1, colors.index(data.card.color)] -= 1
                deckAvailableOthers[data.card.value - 1, colors.index(data.card.color)] -=1
                self.newStates(data.card.value - 1, colors.index(data.card.color))
            else:
                self.toServe.append(data.lastPlayer)
                for i in range(len(self.teammates[data.lastPlayer])):
                    if(self.teammates[data.lastPlayer][i][0] == (data.card.value) and self.teammates[data.lastPlayer][i][1] == data.card.color and data.cardHandIndex == i):
                        self.newStates(data.card.value-1,colors.index(data.card.color))
                        self.teammates[data.lastPlayer].pop(i)
                        self.teammates[data.lastPlayer].append([0,"", Card()])
        elif(type(data) is GameData.ServerHintData ):  ##hint has been given, update local cards
            if data.destination == self.name:
                for i in range(len(self.hand)):
                    self.hand[i].calcHint(data, i, self.deckAvailableSelf)                  #need to update all cards and available cards
            else:
                for i in range(len(self.hand)):
                    self.teammates[data.destination][i][2].calcHint(data, i, deckAvailableOthers)
    
    def criticalHint(self):

        moveType = {
                "type":"hint",
                "hintType":"",
                "player":"",
                "value":0,
                "cards":0,    
                "critical":[],
                "playable":[],
                "cardValue":[],
                "cardColor": []
            }

        

        for key in self.teammates.keys():
            hand = self.teammates[key]
            for c in hand:
                #checks if card is critical #c[0]-1 is the value  #colors.index(c[1]) is the color
                #if state is >2 means that is critical
                #we also check if the hint was already given by checking the probabilities theorized about the other player
                if self.states[c[0]-1,colors.index(c[1])] > 2 and c[2].probs[c[0]-1,colors.index(c[1])]!=0 and c[2].probs[c[0]-1,colors.index(c[1])]!=1:
                    
                    append=0
            #we check if the sum of the values probabilities is 0 or 1, that would mean we have already hinted that value
                    if c[2].value==0 and np.sum(c[2].probs[c[0]-1])!=0 and np.sum(c[2].probs[c[0]-1])<1:
                        move = copy.deepcopy(moveType)
                        move["player"] = key
                        move["cards"] = 1
                        move["critical"].append(1)
                        move["playable"].append(int(self.states[c[0]-1,colors.index(c[1])]==4))
                        move["cardValue"].append(c[0])
                        move["cardColor"].append(c[1])
                        move["hintType"] = "value" 
                        move["value"] = c[0]

                #if we already calculated a certain hint we don't add it as new hint, but merge it to the existing one
                        for hint in hintMoves:
                            if hint["player"] == move["player"] and hint["hintType"] == move["hintType"] and hint["value"] == move["value"]:
                                hint["cards"]+=1
                                hint["critical"].append(1)
                                hint["playable"].append(int(self.states[c[0]-1,colors.index(c[1])]==4))
                                hint["cardValue"].append(c[0])
                                hint["cardColor"].append(c[1])
                                append=1
                                break
                        if append==0:
                            hintMoves.append(move)        

                   #same checks as before but for the color 
                    elif c[2].color=="" and np.sum(c[2].probs[:, colors.index(c[1])])!=0 and np.sum(c[2].probs[:, colors.index(c[1])])<1:
                        append=0
                        move2 = copy.deepcopy(moveType)
                        move2["player"] = key
                        move2["cards"] = 1
                        move2["critical"].append(1)
                        move2["playable"].append(int(self.states[c[0]-1,colors.index(c[1])]==4))
                        move2["cardValue"].append(c[0])
                        move2["cardColor"].append(c[1])
                        move2["hintType"] = "color"
                        move2["value"] = c[1]
                        
                        for hint in hintMoves:
                            if hint["player"] == move2["player"] and hint["hintType"] == move2["hintType"] and hint["value"] == move2["value"]:
                                hint["cards"]+=1
                                hint["critical"].append(1)
                                hint["playable"].append(int(self.states[c[0]-1,colors.index(c[1])]==4))
                                hint["cardValue"].append(c[0])
                                hint["cardColor"].append(c[1])
                                append=1
                                break
                        if append ==0:
                            hintMoves.append(move2) 

        return

    def playableHint(self):
    
        moveType = {
                "type":"hint",
                "hintType":"",
                "player":"",
                "value":0,
                "cards":0,    
                "critical":[],
                "playable":[],
                "cardValue":[],
                "cardColor": []
            }


        for key in self.teammates.keys():
            hand = self.teammates[key]
            for c in hand:
                #functioning similar to criticalhint, changes to flags
                if self.states[c[0]-1,colors.index(c[1])] == 2 and c[2].probs[c[0]-1,colors.index(c[1])]!=0 and c[2].probs[c[0]-1,colors.index(c[1])]!=1:
                    append=0
                    if c[2].value==0 and np.sum(c[2].probs[c[0]-1])!=0 and np.sum(c[2].probs[c[0]-1])!=1:
                        move = copy.deepcopy(moveType)
                        move["player"] = key
                        move["cards"] = 1
                        move["critical"].append(0)
                        move["playable"].append(1)
                        move["cardValue"].append(c[0])
                        move["cardColor"].append(c[1])
                        move["hintType"] = "value" 
                        move["value"] = c[0]

                        for hint in hintMoves:
                            if hint["player"] == move["player"] and hint["hintType"] == move["hintType"] and hint["value"] == move["value"]:
                                hint["cards"]+=1
                                hint["critical"].append(0)
                                hint["playable"].append(1)
                                hint["cardValue"].append(c[0])
                                hint["cardColor"].append(c[1])
                                append=1
                                break
                        if append == 0:
                            hintMoves.append(move)
 
                    elif c[2].color=="" and np.sum(c[2].probs[:, colors.index(c[1])])!=0 and np.sum(c[2].probs[:, colors.index(c[1])])!=1:
                        append = 0
                        move2 = copy.deepcopy(moveType)
                        move2["player"] = key
                        move2["cards"] = 1
                        move2["critical"].append(0)
                        move2["playable"].append(1)
                        move2["cardValue"].append(c[0])
                        move2["cardColor"].append(c[1])
                        move2["hintType"] = "color"
                        move2["value"] = c[1]

                        for hint in hintMoves:
                            if (hint["player"] == move2["player"]) and (hint["hintType"] == move2["hintType"]) and (hint["value"] == move2["value"]): 
                                hint["cards"]+=1
                                hint["critical"].append(0)
                                hint["playable"].append(1)
                                hint["cardValue"].append(c[0])
                                hint["cardColor"].append(c[1])
                                append=1
                                break
                        if append == 0:
                            hintMoves.append(move2)          

        return
    
    def discardableHint(self):
        moveType = {
                "type":"hint",
                "hintType":"",
                "player":"",
                "value":0,
                "cards":0,    
                "critical":[],
                "playable":[],
                "cardValue":[],
                "cardColor": []
            }


        for key in self.teammates.keys():
            hand = self.teammates[key]
            for c in hand:
                #functioning similar to criticalhint, changes to flags
                if self.states[c[0]-1,colors.index(c[1])] == 2 and c[2].probs[c[0]-1,colors.index(c[1])]!=0 and c[2].probs[c[0]-1,colors.index(c[1])]!=1:
                    append=0
                    if c[2].value==0 and np.sum(c[2].probs[c[0]-1])!=0 and np.sum(c[2].probs[c[0]-1])!=1:
                        move = copy.deepcopy(moveType)
                        move["player"] = key
                        move["cards"] = 1
                        move["critical"].append(0)
                        move["playable"].append(0)
                        move["cardValue"].append(c[0])
                        move["cardColor"].append(c[1])
                        move["hintType"] = "value" 
                        move["value"] = c[0]

                        for hint in hintMoves:
                            if hint["player"] == move["player"] and hint["hintType"] == move["hintType"] and hint["value"] == move["value"]:
                                hint["cards"]+=1
                                hint["critical"].append(0)
                                hint["playable"].append(0)
                                hint["cardValue"].append(c[0])
                                hint["cardColor"].append(c[1])
                                append=1
                                break
                        if append == 0:
                            hintMoves.append(move)
 
                    elif c[2].color=="" and np.sum(c[2].probs[:, colors.index(c[1])])!=0 and np.sum(c[2].probs[:, colors.index(c[1])])!=1:
                        append = 0
                        move2 = copy.deepcopy(moveType)
                        move2["player"] = key
                        move2["cards"] = 1
                        move2["critical"].append(0)
                        move2["playable"].append(0)
                        move2["cardValue"].append(c[0])
                        move2["cardColor"].append(c[1])
                        move2["hintType"] = "color"
                        move2["value"] = c[1]

                        for hint in hintMoves:
                            if (hint["player"] == move2["player"]) and (hint["hintType"] == move2["hintType"]) and (hint["value"] == move2["value"]): 
                                hint["cards"]+=1
                                hint["critical"].append(0)
                                hint["playable"].append(0)
                                hint["cardValue"].append(c[0])
                                hint["cardColor"].append(c[1])
                                append=1
                                break
                        if append == 0:
                            hintMoves.append(move2)          
        return

    def findMoves(self):
        global population
        population.clear()
        moveType = {
                "card":0,
                "type":"",
                "critical":0,
                "chance":0,
                "value": 0,
                "color":""
            }

        move = moveType.copy()

        for card in self.hand:
            if card.value!=0 and card.color!="":
                move = moveType.copy()
                if self.states[card.value-1, colors.index(card.color)]==2 or self.states[card.value-1, colors.index(card.color)]==4:
                    move["card"]=self.hand.index(card)
                    move["type"]="play"
                    move["chance"]=1
                    move["critical"]= int(self.states[card.value-1, colors.index(card.color)]==4)
                    move["value"]=card.value
                    move["color"]=card.color
                    population.append(move)
                elif self.states[card.value-1, colors.index(card.color)]==1:
                    move["card"]=self.hand.index(card)
                    move["type"]="discard"
                    move["chance"]=1
                    move["value"]=card.value
                    move["color"]=card.color
                    population.append(move)
            elif card.value!=0 and card.color=="":
                cardTmp = copy.deepcopy(card)
                for color in colors:
                    move = moveType.copy()
                    cardTmp.color=color
                    if (self.states[cardTmp.value-1, colors.index(cardTmp.color)]==2 or self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4) and cardTmp.probs[cardTmp.value-1,colors.index(cardTmp.color)]!=0:
                        move["card"] = self.hand.index(card)
                        move["type"] = "play"
                        move["chance"] = cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["critical"] = int(self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4)
                        move["value"]=cardTmp.value
                        move["color"]=cardTmp.color
                        population.append(move)
                    elif self.states[cardTmp.value-1, colors.index(cardTmp.color)]==1 and cardTmp.probs[cardTmp.value-1,colors.index(cardTmp.color)]!=0:
                        move["card"]=self.hand.index(card)
                        move["type"]="discard"
                        move["chance"]=cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["value"]=cardTmp.value
                        move["color"]=cardTmp.color
                        population.append(move)
            elif card.value==0 and card.color!="":
                cardTmp = card.copy()
                for i in range(5):
                    move = moveType.copy()
                    cardTmp.value=i+1
                    if (self.states[cardTmp.value-1, colors.index(cardTmp.color)]==2 or self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4) and cardTmp.probs[i,colors.index(cardTmp.color)]!=0:
                        move["card"] = self.hand.index(card)
                        move["type"] = "play"
                        move["chance"] = card.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["critical"] = int(self.states[cardTmp.value-1, colors.index(cardTmp.color)]==4)
                        move["value"]=cardTmp.value
                        move["color"]=cardTmp.color
                        population.append(move)
                    elif self.states[card.value-1, colors.index(cardTmp.color)]==1 and cardTmp.probs[i,colors.index(cardTmp.color)]!=0:
                        move["card"]=self.hand.index(card)
                        move["type"]="discard"
                        move["chance"]=cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["value"]=cardTmp.value
                        move["color"]=cardTmp.color
                        population.append(move)
            elif card.value==0 and card.color=="":
                m = card.mask(card.probs, self.states)
                cardTmp = card.copy()
                for i in range(5):
                    for j in range(5):
                        move = moveType.copy()
                        cardTmp.value=i+1
                        cardTmp.color=colors[j]
                        if (m[cardTmp.value-1, colors.index(cardTmp.color)]==2 or m[cardTmp.value-1, colors.index(cardTmp.color)]==4) and cardTmp.probs[i,j]!=0:
                            move["card"] = self.hand.index(card)
                            move["type"] = "play"
                            move["chance"] = cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                            move["critical"] = int(m[cardTmp.value-1, colors.index(cardTmp.color)]==4)
                            move["value"]=cardTmp.value
                            move["color"]=cardTmp.color
                            population.append(move)
                        elif m[cardTmp.value-1, colors.index(cardTmp.color)]==1 and cardTmp.probs[i,j]!=0:
                            move["card"]=self.hand.index(card)
                            move["type"]="discard"
                            move["chance"]=cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                            move["value"]=cardTmp.value
                            move["color"]=cardTmp.color
                            population.append(move)

    def discardIfAllCritical(self):
        global population
        population.clear()
        moveType = {
                "card":0,
                "type":"",
                "critical":0,
                "chance":0,
                "value": 0,
                "color":""
            }

        move = moveType.copy()

        for card in self.hand:
            if card.value!=0 and card.color!="":
                move = moveType.copy()
                move["card"]=self.hand.index(card)
                move["type"]="discard"
                move["chance"]=1
                move["value"]=card.value
                move["color"]=card.color
                population.append(copy.deepcopy(move))
            elif card.value!=0 and card.color=="":
                cardTmp = copy.deepcopy(card)
                for color in colors:
                    move = moveType.copy()
                    cardTmp.color=color
                    move["card"]=self.hand.index(card)
                    move["type"]="discard"
                    move["chance"]=cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                    move["value"]=cardTmp.value
                    move["color"]=cardTmp.color
                    population.append(copy.deepcopy(move))
            elif card.value==0 and card.color!="":
                cardTmp = copy.deepcopy(card)
                for i in range(5):
                    move = moveType.copy()
                    cardTmp.value=i+1
                    move["card"]=self.hand.index(card)
                    move["type"]="discard"
                    move["chance"]=cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                    move["value"]=cardTmp.value
                    move["color"]=cardTmp.color
                    population.append(copy.deepcopy(move))
            elif card.value==0 and card.color=="":
                cardTmp = copy.deepcopy(card)
                for i in range(5):
                    for j in range(5):
                        move = moveType.copy()
                        cardTmp.value=i+1
                        cardTmp.color=colors[j]
                        move["card"]=self.hand.index(card)
                        move["type"]="discard"
                        move["chance"]=cardTmp.probs[cardTmp.value-1, colors.index(cardTmp.color)]
                        move["value"]=cardTmp.value
                        move["color"]=cardTmp.color
                        population.append(copy.deepcopy(move))

    def play(self):

        hintMoves.clear()

        self.findMoves()
        if hint<8:
            self.playableHint()
            self.criticalHint()
        if len(hintMoves) == 0 and hint < 8:
            self.discardableHint()
        if len(population) == 0 and len(hintMoves) == 0:
            self.discardIfAllCritical()

        move = selectMoves(population, hintMoves, hint, errors, self.hand, self.states)
        if move[0]["type"]!="hint":
            self.hand.pop(move[0]["card"])
            self.hand.append(Card())
            self.hand[-1].calcProb(self.deckAvailableSelf)
        
        return move