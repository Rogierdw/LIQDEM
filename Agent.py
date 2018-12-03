import numpy as np

def agent_search(heuristic, landscape, idx, value):
    i = 0
    val = value
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
        self.heuristic = heuristic
        self.links = []
        self.cycle_links = []
        i = 0
        self.ability = np.zeros(len(world))
        self.error = np.zeros(len(world))

        for landscape in world:
            top = max(landscape)
            ab_id = np.zeros(len(landscape))
            for id in range(len(ab_id)):
                ab_id[id] = agent_search(heuristic, landscape, id, landscape[id]) # ab_id is the ability for each starting position
            self.ability[i] = np.mean(ab_id)
            self.error[i] = (top - self.ability[i])*100/top
            i += 1
        #print(self.id)
        #print(self.ability)

    def add_link(self, x):
        self.links.append(x)

    def clear_links(self):
        self.links = []
