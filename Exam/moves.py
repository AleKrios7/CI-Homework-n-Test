import numpy as np
import copy

def mask(probs, deck):
        res2 = np.ma.make_mask(probs)
        res3 = np.ma.masked_array(deck, np.invert(res2), fill_value=0)
        return res3.filled()
        

def selectMoves(population, hintMoves, hint, errors, hand, states):

    availableMoves = []
    #p = (8-hint)/8
    p = 1/(8.5-hint) - 1/8.5
    if hint > 7:
        p +=1
    #proporzionalità inversa su hint disponibili

    #e = (5 + errors*7)/(5 - errors) 
    e = 3**errors

    population = sorted(population, key = lambda p: (p["card"], p["type"]), reverse = False)
    plavMoves = playCard(population, hand, e, p, hint)
    plavMoves = sorted(plavMoves, key = lambda p: p["reward"], reverse = True)
    availableMoves.extend(plavMoves[0:2])
    if hint != 8:
        hintMoves = sendHint(hintMoves, p)
        hintMoves = sorted(hintMoves, key = lambda p: p["reward"], reverse = True)
        availableMoves.extend(hintMoves[0:2])
    
    probsMoves = []
    total = 0
    availableMoves = sorted(availableMoves, key = lambda p: p["reward"], reverse = True)
    offset = availableMoves[-1]["reward"]
    if availableMoves[0]["reward"] > 0 and offset < 0:
        availableMoves = list(filter(lambda m : m["reward"]>0.0, availableMoves)) #something doesn't work here
    elif availableMoves[0]["reward"] < 0:
        tmp = []
        tmp.append(availableMoves[0])
        availableMoves.clear()
        availableMoves.append(tmp[0])
    for key in availableMoves:
        total += key["reward"]+offset*(-1)*int(availableMoves[0]["reward"] < 0)
    
    for key in availableMoves:
        probsMoves.append((key["reward"]+offset*(-1)*int(availableMoves[0]["reward"] < 0))/total)

    move = np.random.choice(availableMoves, 1, probsMoves)

    return move

def playCard(population, hand, e, p, hint):
    
    # move = {
    #             "card":0,
    #             "type":"",
    #             "critical":0,
    #             "chance":0,
    #         }
    #bonuses and penalties
    losePoints = 0
    playmoves = []

    for key in population:
        if key["type"] == "play":
            if len(playmoves)>0 and playmoves[-1]["card"] == key["card"] and playmoves[-1]["type"]=="play":
                playmoves[-1]["chance"]+=key["chance"]
                b=-1
            elif len(playmoves)>1 and playmoves[-2]["card"] == key["card"] and playmoves[-1]["type"]=="play":
                playmoves[-2]["chance"]+=key["chance"]
                b=-2
            else:
                playmoves.append(copy.deepcopy(key))
                b=-1

            if key["critical"] == 1:
                losePoints = 6 - key["value"]
                if key["value"] == 5:
                    playmoves[b]["reward"] = playmoves[b]["chance"]*(1 + p*2)-(1-playmoves[b]["chance"])*e*(losePoints+1)
                else:
                    playmoves[b]["reward"] = playmoves[b]["chance"]-(1-playmoves[b]["chance"])*e*(losePoints+1)
            else:
                if key["value"] == 5:
                    playmoves[b]["reward"] = playmoves[b]["chance"]*(1+p*2)-(1-playmoves[b]["chance"])*e
                else:
                    playmoves[b]["reward"] = playmoves[b]["chance"]*(1+p*2)-(1-playmoves[b]["chance"])*e
        elif key["type"] == "discard" and hint!=8:
            if len(playmoves)>0 and playmoves[-1]["card"] == key["card"] and playmoves[-1]["type"]=="discard":
                playmoves[-1]["chance"]+=key["chance"]
                b=-1
            elif len(playmoves)>1 and playmoves[-2]["card"] == key["card"] and playmoves[-1]["type"]=="discard":
                playmoves[-2]["chance"]+=key["chance"]
                b=-2
            else:
                b=-1
                playmoves.append(copy.deepcopy(key))

            
            if key["critical"] == 1:
                losePoints = 6 - hand[key["card"]].value
                playmoves[b]["reward"] = playmoves[b]["chance"]*(p)-(1-playmoves[b]["chance"])*(losePoints+1)
            else:
                playmoves[b]["reward"] = playmoves[b]["chance"]*(p)-(1-playmoves[b]["chance"])

    return playmoves
    
def sendHint(hintMoves, p):
    
    # move = {
    #         "type":"",
    #         "hintType":"",
    #         "player":"",
    #         "value":0,
    #         "cards":[],    
    #         "critical":[],
    #         "playable":[],
    #         "cardValue":[],
    #         "cardColor": []
    #         }
    criticalSignal = 0
    bonusPoints = 0

    for m in hintMoves:
        tot = 0
        pointsaved = 0
        aff = 1.3
        for i in range(m["cards"]):
            if m["critical"][i] == 1 and m["playable"][i] == 1:
                pointsaved += 6 - m["cardValue"][i] + 1 +2*p*(1 if m["cardValue"][i] == 5 else 0)
                bonusPoints += 1
                
            elif m["critical"][i] == 1:
                pointsaved += 6 - m["cardValue"][i]
                bonusPoints+=.5

            else:
                pointsaved += 1 +2*p*(m["cardValue"] == 5)
        tot += aff * pointsaved - 2*p + bonusPoints
        m["reward"] = tot
    return hintMoves