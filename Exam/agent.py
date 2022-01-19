from multiprocessing.sharedctypes import Value
import GameData
import numpy as np

players=0
colors = ["red","white","blue","yellow","green"]
deckAvailable = np.array([[3,3,3,3,3],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[1,1,1,1,1]], dtype="uint")

class Card(object):
    def __init__() -> None:
        super().__init__()

    value = 0
    color = ""
    probs= np.array([
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1]
    ], dtype="float")
    state=""        

hand = []



def mngmnt(data):
    global players

    if players == 0:
        players = data.connectedPlayers
        if data.connectedPlayers == 2 or data.connectedPlayers == 3:
            for i in range(5):
                hand.append(Card())
        else:
            for i in range(4):
                hand.append(Card())
    return

def move():
    veryintelligentmove = "show"
    return veryintelligentmove