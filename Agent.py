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
        self.links = []
        i = 0
        self.ability = np.zeros(len(world))
        self.error = np.zeros(len(world))
        for landscape in world:
            top = max(landscape)
            ab_id = np.zeros(len(landscape))
            for id in range(len(ab_id)):
                ab_id[id] = agent_search(heuristic, landscape, id, landscape[id]) # ab_id is the ability for each starting position
            self.ability[i] = np.mean(ab_id)
            self.error[i] = (top - self.ability[i])/top *100
            i += 1
        #print(self.id)
        #print(self.ability)

    def add_link(self, x):
        self.links.append(x)

    def clear_links(self):
        self.links = []

'''
    def create_links(self, amount, net_type, degree = 20):
        ##DEPRECATED, USE create_network in WORLD.PY
        ### LIQUID VERSION
        self.links = []
        #p = 1/(amount^2)
        #p = 1 / amount

        if net_type == 'fully':
            self.links = range(1, amount + 1)

        if net_type == 'random':
            self.links.append(self.id)
            p = degree / amount
            for id in range(1, amount+1):
                if id == self.id:
                    continue
                elif p >= random():
                    self.links.append(id)

            
            OLD RANDOM BLOCK 2
            i = 0
            while i < degree:
                new = randint(1,amount)
                if new not in self.links:
                    self.links.append(new)
                    i += 1
            
            OLD RANDOM BLOCK 1
            for id in range(1, amount + 1):
                if id==self.id:
                    continue
                else:
                    
                    if p >= random():
                        self.links.append(id)
            

        if net_type == 'regular':
            self.links.append(self.id)
            i = 0
            while i < degree:
                new = randint(1, amount)
                if new not in self.links:
                    self.links.append(new)
                    i += 1

        if net_type == 'ring':
            self.links.append(self.id)
            id = self.id + amount
            lis = range(id - int(degree/2), id + int(degree/2) + 1)
            for it in lis:
                if it % amount == self.id:
                    continue
                elif it%amount == 0:
                    self.links.append(amount)
                else:
                    self.links.append(it%amount)

        if net_type == 'small':
            self.links.append(self.id)
            p = 0.25
            holder = []
            id = self.id + amount
            lis = range(id - int(degree / 2), id + int(degree / 2) + 1)
            for it in lis:
                if it % amount == self.id:
                    continue
                elif it % amount == 0:
                    holder.append(amount)
                else:
                    holder.append(it % amount)

            for item in holder:
                if p >= random():
                    new = randint(1,amount)
                    if new not in holder and new not in self.links and new != self.id:
                        self.links.append(new)
                    else:
                        self.links.append(item)
                else:
                    self.links.append(item)
        #print(self.links)
'''