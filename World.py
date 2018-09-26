from random import randint, random
from math import floor,ceil
from Agent import Agent
import numpy as np
import itertools

def landscape(size, min, max, SF):
    if SF == 0:
        return [randint(min, max) for _ in range(size)]
    else:
        subj = [0 for _ in range(size)]
        i = 0
        br = False
        subj[i] = randint(min, max)
        while (i < size):

            add = randint(1, 2 * SF + 1)  # Next integer
            j = i + add
            if (j >= size):  # End of circle
                j = 0
                diff_idx = size - i
                br = True
            else:  # Next point on circle
                subj[j] = randint(min, max)
                diff_idx = j - i

            if(diff_idx > 1):  # Filling integers
                k = 1
                diff = subj[j] - subj[i]
                change = diff / diff_idx
                flo = floor(change)
                cei = ceil(change)
                while(k < diff_idx):
                    if(k%2==0):
                        subj[i + k] = subj[i+k-1] + flo
                    else:
                        subj[i + k] = subj[i + k - 1] + cei
                    k += 1
            if br:
                break
            else:
                i = j
        return subj

def create_agents(world, heur_size = 3, heur_max = 12):
    amount = int(np.math.factorial(heur_max) / np.math.factorial(heur_max - heur_size))
    print('num.Agents = ' + str(amount))
    agents = []
    id_list = np.random.permutation(range(1,amount+1))
    id = 0
    while id < amount:
        for i in range(1, heur_max + 1):
            for j in range(1, heur_max + 1):
                for k in range(1, heur_max + 1):
                    if i != j and i != k and j !=k:
                        new_agent = Agent(id_list[id], (i, j, k), world)
                        agents.append(new_agent)
                        id += 1
    return agents, amount



class World():
    def __init__(self, subjects, size, min, max):
        self.subjects = subjects
        #OLD, SET SMOOTHING
        #self.world = [landscape(size,min,max,SF=3) for _ in range(subjects)]
        #NEW, Ramping smoothing
        self.world = []
        for SF in range(subjects):
            self.world.append(landscape(size=size, min=min, max=max, SF=SF))
        self.agents, self.amount = create_agents(self.world)

    def direct(self):
        #DIRECT DEMOCRACY!!!
        print("\nDIRECT DEMOCRACY")
        a = [agent.ability for agent in self.agents]
        print(np.mean(a,0))

    def liquid(self, net_type):
        print('\nLIQUID DEMOCRACY')
        print('Network type = ' + net_type)
        self.create_network(net_type)

        ## Each agent determines links with highest ability (best_links)
        self.search_best_links()

        ## Delegation of votes in while loop
        voting_power = np.ones([len(self.agents), self.subjects])
        DELEGATE = True
        while DELEGATE:
            DELEGATE = False
            for agent in self.agents:
                for idx in range(self.subjects):
                    if voting_power[agent.id-1][idx] != 0:
                        if agent.best_links[idx] != agent.id:
                            DELEGATE = True
                            deleg = voting_power[agent.id-1][idx]
                            voting_power[agent.id-1][idx] = 0
                            voting_power[agent.best_links[idx]-1][idx] += deleg

        ## Calculation of weighted voting power of agents
        b = np.zeros(self.subjects)
        for idx in range(self.subjects):
            aggregation = 0
            for agent in self.agents:
                if voting_power[agent.id-1][idx] != 0:
                    b[idx] += voting_power[agent.id-1][idx] * agent.ability[idx]
                    aggregation += voting_power[agent.id-1][idx]
            b[idx] = b[idx] / aggregation

        print(b)

    def create_network(self, net_type):
        # Agent network creation LIQUID VERSION
        if net_type=='power':
            self.create_power_network(1) ## MAGIC NUMBER!
        else:
            for agent in self.agents:
                agent.create_links(self.amount, net_type)

    def search_best_links(self):
        ### LIQUID VERSION, searches agent.links
        for agent in self.agents:
            #agent.best_links = []
            x = np.empty([0,len(agent.ability)])
            for link in agent.links:
                for agent2 in self.agents:
                    if agent2.id == link:
                        x = np.vstack([x, agent2.ability])
            agent.best_links = [agent.links[i] for i in np.argmax(x, axis=0)] # argmax calcs best abilities in x, list comprehension gives the best_link ids
            #print(agent.best_links)

    def create_power_network(self, start_m):
        x = 0
        lis = []
        network = []
        for agent in self.agents:
            if x < start_m:
                lis.append(agent.id)
            if x == start_m:
                for i in range(start_m):
                    network.append(lis[i:start_m]+lis[0:i])
            if x >= start_m:
                # m_0 is set up, now for the real deal
                Success = False
                while not Success:
                    i = randint(0,len(network)-1)
                    k_i = len(network[i])
                    k_tot = len(list(itertools.chain.from_iterable(network)))
                    p = k_i / k_tot
                    if p > random():
                        Success = True
                        network[i].extend([agent.id])
                        network.append([agent.id, i])
            x+=1

        x = 0
        for agent in self.agents:
            agent.links = network[x]
            x+=1
