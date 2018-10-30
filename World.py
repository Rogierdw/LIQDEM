from random import randint, uniform
from math import floor,ceil
from copy import copy
from Agent import Agent
import numpy as np
import networkx as nx

DEBUG = True

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

def create_agents(world, heur_size = 3, heur_max = 12, percentage = 100):
    amount = int(np.math.factorial(heur_max) / np.math.factorial(heur_max - heur_size))
    if not percentage==100:
        num = int(amount*percentage/100)
    else:
        num = amount


    if DEBUG:
        print('num.Agents = ' + str(num))
    agents = []
    id_list = range(0,amount)
    id = 0
    while id < amount:
        for i in range(1, heur_max + 1):
            for j in range(1, heur_max + 1):
                for k in range(1, heur_max + 1):
                    if i != j and i != k and j !=k:
                        new_agent = Agent(id_list[id], (i, j, k), world)
                        agents.append(new_agent)
                        id += 1
    # If percentage is 100, agent sample will just have all agents, but shuffeled.
    agents_sample = []
    for i in range(num):
        agent = agents.pop(randint(0,len(agents)-1))
        agent.id = i
        agents_sample.append(agent)
    return agents_sample, num

def calc_diversity(agent1, agent2):
    k = len(agent1.heuristic) ## NOTE THAT the assumption is that both heuristics are of length k
    delta = 0
    for i in range(k):
        if agent1.heuristic[i]+i == agent2.heuristic[i]+i:  # delta(sig_a, sig_b) = 1 if sig_a(i) == sig_b(i)
            delta += 1
    return float(k-delta)/k

def calc_population_diversity(agent_list):
    if DEBUG:
        print('Calculating population diversity')
    divs = []
    while len(agent_list) > 1:
        agent1 = agent_list.pop(0)
        for i in range(len(agent_list)):
            agent2 = agent_list[i]
            divs.append(calc_diversity(agent1, agent2))
    return np.mean(divs)



class World():
    def __init__(self, subjects, size, min, max, percentage, PRINT):
        self.PRINT = PRINT
        self.subjects = subjects
        #OLD, SET SMOOTHING
        #self.world = [landscape(size,min,max,SF=3) for _ in range(subjects)]
        #NEW, Ramping smoothing
        self.world = []
        for SF in range(subjects):
            self.world.append(landscape(size=size, min=min, max=max, SF=SF))
        self.agents, self.amount = create_agents(self.world, percentage=percentage)

    def direct(self):
        #DIRECT DEMOCRACY!!!
        if self.PRINT:
            print("\nDIRECT DEMOCRACY")

        a = [agent.ability for agent in self.agents]
        res = np.mean(a,0)
        a_e = [agent.error for agent in self.agents]
        err = np.mean(a_e, 0)
        div = calc_population_diversity(copy(self.agents))

        if self.PRINT:
            print('Ability results')
            print(res)
            print('Error percentages')
            print(err)
            print('Diversity')
            print(div)

        return(res, err, div)

    def representative_abil(self, degree):
        c = [(agent.id, np.mean(agent.ability)) for agent in self.agents]
        id_list = []

        for _ in range(degree):
            c_argmax = np.argmax(c, 0)[1] #Spot of highest avg abil
            id_list.append(c.pop(c_argmax)[0]) # pop highest avg ability, add id to list

        ac_list = []
        er_list = []
        ag_list = []
        for agent in self.agents:
            if agent.id in id_list:
                ac_list.append(agent.ability)
                er_list.append(agent.error)
                ag_list.append(agent)
        res = np.mean(ac_list,0)
        err = np.mean(er_list,0)
        div = calc_population_diversity(ag_list)

        if self.PRINT:
            print("\nREPRESENTATIVE DEMOCRACY - Highest Ability")
            print('Ability results')
            print(res)
            print('Error percentages')
            print(err)
            print('Div_vote')
            print(div)

        return (res, err, div)

    def representative_rand(self, degree):
        c = [(agent.id, np.mean(agent.ability)) for agent in self.agents]
        id_list = []
        for _ in range(degree):
            id_list.append(c.pop(randint(0,len(c)-1))[0]) # pop highest avg ability, add id to list

        ac_list = []
        er_list = []
        ag_list = []
        for agent in self.agents:
            if agent.id in id_list:
                ac_list.append(agent.ability)
                er_list.append(agent.error)
                ag_list.append(agent)
        res = np.mean(ac_list, 0)
        err = np.mean(er_list, 0)
        div = calc_population_diversity(ag_list)

        if self.PRINT:
            print("\nREPRESENTATIVE DEMOCRACY - Random Ability")
            print('Ability results')
            print(res)
            print('Error percentages')
            print(err)
            print('Div_vote')
            print(div)

        return (res, err, div)

    def liquid(self, net_type, degree=20, epsilon=0):
        if self.PRINT:
            print('\nLIQUID DEMOCRACY')
            print('Network type = ' + net_type)
        self.create_network(net_type, degree)
        ## Each agent determines links with highest ability (best_links)
        self.search_best_links(epsilon=epsilon)

        if DEBUG:
            print('mean degree: ' + str(np.mean([len(agent.links) for agent in self.agents]) - 1))
            print('starting delegation of votes')

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
        b_e = np.zeros(self.subjects)
        div_a = np.zeros(self.subjects)
        wdiv_a = np.zeros(self.subjects)

        for idx in range(self.subjects):
            div = []
            wdiv = []
            aggregation = 0
            for agent in self.agents:
                if voting_power[agent.id-1][idx] != 0:
                    b[idx] += voting_power[agent.id-1][idx] * agent.ability[idx]
                    b_e[idx] += voting_power[agent.id-1][idx] * agent.error[idx]
                    aggregation += voting_power[agent.id-1][idx]

                    div.append(agent)
                    wdiv.extend([agent for i in range(int(voting_power[agent.id-1][idx]))])

            b[idx] = b[idx] / aggregation
            b_e[idx] = b_e[idx] / aggregation

            div_a[idx] = calc_population_diversity(div)
            wdiv_a[idx] = calc_population_diversity(wdiv)

        if self.PRINT:
            print('Ability results')
            print(b)
            print('Error percentages')
            print(b_e)
            print('Div_vote')
            print(div_a)
            print('WDiv_vote')
            print(wdiv_a)

        return (b, b_e, div_a, wdiv_a)

    def create_network(self, net_type, degree):
        #print('NetworkX creating network')
        if net_type == 'fully':
            G = nx.complete_graph(self.amount)

        if net_type == 'random':
            G = nx.fast_gnp_random_graph(self.amount, degree/self.amount)
            while not nx.is_connected(G):
                G = nx.fast_gnp_random_graph(self.amount, degree / self.amount)

        if net_type == 'regular':
            G = nx.random_regular_graph(degree, self.amount)
            while not nx.is_connected(G):
                G = nx.random_regular_graph(degree, self.amount)

        if net_type == 'ring':
            G = nx.connected_watts_strogatz_graph(n=self.amount, k=degree, p=0)
            while not nx.is_connected(G):
                G = nx.connected_watts_strogatz_graph(n=self.amount, k=degree, p=0)

        if net_type == 'small':
            G = nx.connected_watts_strogatz_graph(n=self.amount, k=degree, p=0.25)
            while not nx.is_connected(G):
                G = nx.connected_watts_strogatz_graph(n=self.amount, k=degree, p=0.25)

        if net_type == 'scale free':
            G = nx.barabasi_albert_graph(n=self.amount, m=int(degree/2))
            while not nx.is_connected(G):
                G = nx.barabasi_albert_graph(n=self.amount, m=int(degree / 2))

        if DEBUG:
            print('Network created')
            print('number of nodes: '+str(G.number_of_nodes()))
            print('number of edges: '+str(G.number_of_edges()))
        self.from_graph_to_links(G.edges())


        '''
        # Agent network creation LIQUID OWN VERSION, DEPRECATED
        if net_type=='scale free':
            self.create_scale_free_network(int(degree/2))
        else:
            for agent in self.agents:
                agent.create_links(self.amount, net_type, degree)
        '''

    def from_graph_to_links(self, edges):
        if DEBUG:
            print('starting conversion from graph to links')
        for agent in self.agents:
            agent.clear_links()
            for edge in edges:
                if agent.id in edge:
                    if edge[0] not in agent.links:
                        agent.add_link(edge[0])
                    if edge[1] not in agent.links:
                        agent.add_link(edge[1])
            if len(agent.links)==0:
                print('ERROR: AGENT HAS NO LINKS:')
                print(agent.id, agent.links)
                print('total agents in sample: ' + str(self.amount))
                quit()

    def search_best_links(self, epsilon):
        ### LIQUID VERSION, searches agent.links
        if DEBUG:
            print('searching for best links of agents')

        for agent in self.agents:
            #agent.best_links = []
            x = np.empty([0,len(agent.ability)])
            for link in agent.links:
                for agent2 in self.agents:
                    if link == agent2.id:
                        ab = agent2.ability
                        for i in range(len(ab)):
                            ab[i] = ab[i] + uniform(-epsilon, epsilon)
                        x = np.vstack([x, ab])
            agent.best_links = [agent.links[i] for i in np.argmax(x, axis=0)] # argmax calcs best abilities in x, list comprehension gives the best_link ids
            #print(agent.best_links)
