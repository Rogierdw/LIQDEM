import numpy as np

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
