from multiprocessing.sharedctypes import Value
import GameData
import numpy as np

players=0
colors = ["red","white","blue","yellow","green"]
moveTypes = ["play","hint","discard"]

class Card(object):
        def __init__() -> None:
            super().__init__()
            
        value = 0
        color = ""
        probs = np.array([   #row = value  column = color
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1]
        ], dtype="float")
        state=""     
        
        def calcProb(deck):
            #calcolo probabilità cambiamento del deck (play/discard)
            print("lul")
        
        def calcHint(self, hint, mypos):
            #calcolo probabilità ricezione indizi (hint)
            #hint.type             value o color (type)
            #hint.destination      player to
            #hint.value            number or string (effective value)
            #hint.positions        array delle posizioni
            if hint.type == "value":
                if mypos in hint.positions:
                    self.value = hint.value
                    for i in range(5): #values
                        if i != mypos:
                            self.probs[i].fill(0) # TODO: fill only not rows with 0s, set new probabilities of yes row
                else:
                    print("")


##TODO fix function to reset probabilities for wrong colors
            elif hint.type == "color":
                if mypos in hint.positions:
                    self.color = hint.value
                    for i in range(5):
                        if i != mypos:
                            self.probs[i][mypos] = 0

            print("lel")


class Player(object):  
    hand = []
    name = ""
    isMe = -1
    

    deckAvailableSelf = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")
    deckAvailableOthers = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")

    def __init__(self, cards, me) -> None:
        super().__init__()
        isMe = me
        for _ in range(cards):
            self.hand.append(Card())

    def mngmnt(data):
        if type(data) is GameData.ServerGameStateData:
            print("lul")
        return

    def play(index):
        print("To implement")

    def discard(index):
        print("To implement")
    
    def move():
        veryintelligentmove = "show"
        return veryintelligentmove
    
    def update(self, data):  #entra qui se ricevo hint o se qualcuno/io gioco/scarto
        print("Robe") #aggiorna saved decks
        if(type(data) is GameData.ServerGameStateData):                         ##show has been called, update is needed
            #TODO: modifica deck values using data
            #change single hand cards probabilities
            for i in range(len(self.hand)):
                self.hand[i].calcProb(self.deckAvailableSelf)
        elif(type(data) is GameData.ServerHintData and data.destination == self.name):                            ##hint has been given, update local cards
            for i in range(len(self.hand)):
                self.hand[i].calcHint(data, i)

        #discard commands
        type(data) is GameData.ServerActionValid #discard
        type(data) is GameData.ServerActionInvalid #wrong command

        #play commands
        type(data) is GameData.ServerPlayerMoveOk #correct play
        type(data) is GameData.ServerPlayerThunderStrike #wrong move

        #error msg
        type(data) is GameData.ServerInvalidDataReceived #invalid data

        #game setup commands
        type(data) is GameData.ServerGameOver #game over
        type(data) is GameData.ServerPlayerStartRequestAccepted #start request (queue)
        type(data) is GameData.ServerStartGameData #ready

        #for i in range(len(self.hand)):
        #   self.hand[i].calcProb(data, self.deckAvailableSelf)
        #devo decidere che update fare
