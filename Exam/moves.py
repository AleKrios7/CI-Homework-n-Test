import numpy as np
import copy

colors = ["red","white","blue","yellow","green"]

def selectMoves(population, hintMoves, hint, errors, hand, states):

    availableMoves = []
    p = 1/(8.5-hint) - 1/8.5
    if hint > 7:
        p *=2
    #proporzionalità inversa su hint disponibili

    #e = (5 + errors*7)/(5 - errors) 
    e = 3**errors +1

    if hint == 0:
        population = list(filter(lambda n : n["type"] == "play", population))
    population = sorted(population, key = lambda p: (p["card"], p["type"]), reverse = False)
    population = playCard(population, hand, e, p, hint, states)
    population = sorted(population, key = lambda p: p["reward"], reverse = True)
    
    if hint != 8:
        hintMoves = sendHint(hintMoves, p)
        hintMoves = sorted(hintMoves, key = lambda p: p["reward"], reverse = True)
        
    availableMoves.extend(population)
    availableMoves.extend(hintMoves)
    availableMoves = sorted(availableMoves, key = lambda p: p["reward"], reverse = True)
    availableMoves = list(filter(lambda b : availableMoves[0]["reward"]-b["reward"]<=1, availableMoves))
    probsMoves = []
    total = 0

    offset = availableMoves[-1]["reward"]
    if availableMoves[0]["reward"] > 0 and offset < 0:
        availableMoves = list(filter(lambda m : m["reward"]>0.0, availableMoves))
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

def playCard(population, hand, e, p, hint, states):

    global colors
    
    # move = {
    #             "card": int, -> index
    #             "type": string, -> play o discard
    #             "critical":[int], -> array di hint
    #             "chance":[float], -> array di probs
    #             "valcol": [(int,string)] -> array di tuple int,string         
    #         }
    #bonuses and penalties

    for mov in population:
        if mov["type"] == "play":
            totreward = 0
            totlosePoints = 0
            #playmoves[b]["reward"] = playmoves[b]["chance"]*(1 + p*2)-(1-playmoves[b]["chance"])*e*(losePoints+1)
            
            for i in range(len(mov["valcol"])):
                if mov["valcol"][i][0] == 5:
                    totreward += (1+p) * mov["chance"][i]
                else:
                    totreward += mov["chance"][i]
            for i in range(5):
                for j in range(5):
                    notInMove = True
                    for k in mov["valcol"]:
                        if (k[0] == i+1 and k[1] == colors[j]):
                            notInMove = False
                    if notInMove and states[i,j] > 2 and hand[mov["card"]].probs[i,j]!=0:
                        totlosePoints += (6- (i+1))*(hand[mov["card"]].probs[i,j])
            mov["reward"] = totreward - totlosePoints - (1-sum(mov["chance"]))*e
            if sum(mov["chance"]) == 1:
                mov["reward"] += 2
        elif hint != 0:
            totreward = 0
            totlosePoints = 0
            for i in range(len(mov["valcol"])):
                if mov["critical"][i] == 1:
                    totreward += (p - (8 - mov["valcol"][i][0]))*mov["chance"][i]  # 6 è da cambiare in un numero più alto
                else:
                    totreward += p*mov["chance"][i]

            for i in range(5):
                for j in range(5):
                    notInMove = True
                    for k in mov["valcol"]:
                        if (k[0] == i+1 and k[1] == colors[j]):
                            notInMove = False
                    if notInMove and states[i,j] > 2 and hand[mov["card"]].probs[i,j]!=0:
                        totlosePoints += (6- (i+1))*(hand[mov["card"]].probs[i,j])
            #playmoves[b]["reward"] = playmoves[b]["chance"]*(p)-(1-playmoves[b]["chance"])*(losePoints+1)
            mov["reward"] = totreward - totlosePoints
    return population

    
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

    for m in hintMoves:
        tot = 0
        pointsaved = 0
        aff = 1
        for i in range(m["cards"]):
            if m["critical"][i] == 1:
                pointsaved += 6 - m["cardValue"][i]
            if m["playable"][i] == 1:
                pointsaved += 1 + p*int(m["cardValue"][i] == 5)
        if pointsaved == 0:
            pointsaved = -0.3
        tot = aff * pointsaved - p
        m["reward"] = tot
    return hintMoves