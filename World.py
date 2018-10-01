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

    def representative(self, degree):
        print("\nREPRESENTATIVE DEMOCRACY - Highest Ability")
        c = [(agent.id, np.mean(agent.ability)) for agent in self.agents]
        id_list = []

        for _ in range(degree):
            c_argmax = np.argmax(c, 0)[1] #Spot of highest avg abil
            id_list.append(c.pop(c_argmax)[0]) # pop highest avg ability, add id to list

        ac_list = []
        for agent in self.agents:
            if agent.id in id_list:
                ac_list.append(agent.ability)
        print(np.mean(ac_list,0))

        print("\nREPRESENTATIVE DEMOCRACY - Random Ability")
        c = [(agent.id, np.mean(agent.ability)) for agent in self.agents]
        id_list = []
        for _ in range(degree):
            id_list.append(c.pop(randint(0,len(c)-1))[0]) # pop highest avg ability, add id to list

        ac_list = []
        for agent in self.agents:
            if agent.id in id_list:
                ac_list.append(agent.ability)
        print(np.mean(ac_list,0))

    def liquid(self, net_type, degree):
        print('\nLIQUID DEMOCRACY')
        print('Network type = ' + net_type)
        self.create_network(net_type, degree)
        print('Average outdegree: ' + str(np.mean([len(agent.links) for agent in self.agents])))
        #print('Average intdegree: ' + str(np.mean([len(agent.inlinks) for agent in self.agents])))

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

    def create_network(self, net_type, degree):
        # Agent network creation LIQUID VERSION
        if net_type=='scale free':
            self.create_scale_free_network(int(degree/2))
        else:
            for agent in self.agents:
                agent.create_links(self.amount, net_type, degree)

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

    def create_scale_free_network(self, m0):
        x = 0
        lis = []
        network = []
        for agent in self.agents:
            #print(str(x) + '/' + str(len(self.agents)) + ' = ' + str(int(x/len(self.agents)*100)) + '%')
            if x < m0:
                lis.append(agent.id)
            if x == m0:
                for i in range(m0):
                    network.append(lis[i:m0]+lis[0:i]) # starting network is fully connected
                k_tot = len(list(itertools.chain.from_iterable(network)))
            if x >= m0:
                # m_0 is set up, now for the real deal
                y = 0
                added = [agent.id]
                while y < m0: # here we take m == m0, so per new agent m0 outdegrees are made
                    i = randint(0, len(network) - 1)
                    k_i = len(network[i])
                    p = k_i / k_tot
                    if p > random() and not i in added:
                        k_tot += 2
                        network[i].extend([agent.id])
                        if y == 0:
                            network.append([agent.id, network[i][0]])
                        else:
                            network[x].append(network[i][0])
                        y += 1
                        added.append(i)
            x+=1

        x = 0
        for agent in self.agents:
            agent.links = network[x]
            x+=1
