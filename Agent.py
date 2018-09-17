import numpy as np
from random import random, randint

def agent_search(heuristic, landscape, idx, val):
    i = 0
    heurs_used = 0
    while heurs_used <= len(heuristic):
        new = landscape[(idx + heuristic[i])%len(landscape)]
        if( new >= val):
            val = new
            idx = (idx + heuristic[i])%len(landscape)
            heurs_used = 0
        else:
            heurs_used += 1
        i = (i + 1)%len(heuristic)
    return(val)



class Agent():
    def __init__(self, id,  heuristic, world):
        self.id = id
        i = 0
        self.ability = np.zeros(len(world))
        for landscape in world:
            ab_id = np.zeros(len(landscape))
            for id in range(len(ab_id)):
                ab_id[id] = agent_search(heuristic, landscape, id, landscape[id])
            self.ability[i] = np.mean(ab_id)
            i += 1
        #print(self.ability)



    def create_links(self, amount, net_type, edges = 8):
        links = []
        #p = 1/(amount^2)
        #p = 1 / amount
        p = 0.1

        if net_type == 'fully':
            links = range(1, amount + 1)

        if net_type == 'random':
            for id in range(1, amount + 1):
                if id==self.id:
                    links.append(id)
                else:
                    if p >= random():
                        links.append(id)

        if net_type == 'regular':
            id = self.id + amount
            lis = range(id - int(edges/2), id + int(edges/2) + 1)
            for it in lis:
                if it%amount == 0:
                    links.append(amount)
                else:
                    links.append(it%amount)

        if net_type == 'small':
            holder = []
            id = self.id + amount
            lis = range(id - int(edges / 2), id + int(edges / 2) + 1)
            for it in lis:
                if it % amount == 0:
                    holder.append(amount)
                else:
                    holder.append(it % amount)

            for item in holder:
                if p >= random():
                    new = randint(1,amount)
                    if new not in holder and new not in links:
                        links.append(new)
                    else:
                        links.append(item)
                else:
                    links.append(item)

        #print(links)
        return links
