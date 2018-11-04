from random import randint, uniform
from copy import copy
from Agent import Agent
import numpy as np
import networkx as nx

DEBUG = False

def landscape(size, min, max, SF):
    if SF == 0:
        return [randint(min, max) for _ in range(size)] # random landscape of size size, integers between min and max
    else:
        subj = [0 for _ in range(size)]                 # intialize all idx to zero
        i = 0
        br = False
        subj[i] = randint(min, max)                     # random value on first idx
        while (i < size):

            add = randint(1, 2 * SF + 1)
            j = i + add                                 # j is next integer for random value
            if (j >= size):                             # End of circle
                j = 0                                   # next point is first point on circle
                diff_idx = size - i
                br = True
            else:                                       # Next point on circle
                subj[j] = randint(min, max)             # random
                diff_idx = add

            if(diff_idx > 1):                           # if i and j are apart, need to fill
                k = i + 1
                diff = subj[j] - subj[i]                #  difference between points
                change = float(diff) / diff_idx         # change per idx
                while (k < i + diff_idx):
                    subj[k] = subj[k-1] + change        # first add change to each previous value
                    k+=1
                k = i + 1
                while (k < i + diff_idx):
                    subj[k] = int(round(subj[k]))       # then round and cast to int
                    k += 1
            if br:
                break                                   # This is done after the intermediate value are filled in
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
    id = 0
    while id < amount:
        for i in range(1, heur_max + 1):
            for j in range(1, heur_max + 1):
                for k in range(1, heur_max + 1):
                    if i != j and i != k and j !=k:
                        new_agent = Agent(id, (i, j, k), world) # new agents, heurs are ordered
                        agents.append(new_agent)
                        id += 1
    # If percentage is 100, agent sample will just have all agents, but shuffeled.
    agents_sample = []
    for i in range(num):
        agent = agents.pop(randint(0,len(agents)-1))        # random agent from agent list is popped
        agent.id = i                                        # new id given, this makes sure the heurs are shuffled
        agents_sample.append(agent)                         # sample list is returned
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
            self.world.append(landscape(size=size, min=min, max=max, SF=2))
        self.agents, self.amount = create_agents(self.world, percentage=percentage)

    def direct(self):
        #DIRECT DEMOCRACY!!!
        if self.PRINT:
            print("\nDIRECT DEMOCRACY")

        err = np.mean([agent.error for agent in self.agents], 0)    # mean of all agent errors
        div = calc_population_diversity(copy(self.agents))          # copy needed so that self.agents stays the same

        if self.PRINT:
            print('Error percentages')
            print(err)
            print('Diversity')
            print(div)

        return(err, div)

    def representative_abil(self, degree):
        c = [(agent.id, np.mean(agent.ability)) for agent in self.agents]
        id_list = []

        for _ in range(degree):
            c_argmax = np.argmax(c, 0)[1] #Spot of highest avg abil
            id_list.append(c.pop(c_argmax)[0]) # pop highest avg ability, add id to list

        er_list = []
        ag_list = []
        for agent in self.agents:
            if agent.id in id_list:
                er_list.append(agent.error)
                ag_list.append(agent)
        err = np.mean(er_list,0)
        div = calc_population_diversity(ag_list)

        if self.PRINT:
            print("\nREPRESENTATIVE DEMOCRACY - Highest Ability")
            print('Error percentages')
            print(err)
            print('Div_vote')
            print(div)

        return (err, div)

    def representative_rand(self, degree):
        c = [agent.id for agent in self.agents]
        id_list = []
        for _ in range(degree):
            id_list.append(c.pop(randint(0,len(c)-1))) # pop random agent, add id to list

        er_list = []
        ag_list = []
        for agent in self.agents:
            if agent.id in id_list:
                er_list.append(agent.error)
                ag_list.append(agent)
        err = np.mean(er_list, 0)
        div = calc_population_diversity(ag_list)

        if self.PRINT:
            print("\nREPRESENTATIVE DEMOCRACY - Random Ability")
            print('Error percentages')
            print(err)
            print('Div_vote')
            print(div)

        return (err, div)

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

        ### Delegation in seperate function!
        voting_power = self.delegation()

        if DEBUG:
            print('Calculate actual voting > weighted mean')
        ## Calculation of weighted voting power of agents
        error = np.zeros(self.subjects)
        diversity = np.zeros(self.subjects)
        weighted_diversity = np.zeros(self.subjects)
        votes_left = np.zeros(self.subjects)



        for idx in range(self.subjects): # actual voting
            div = []
            wdiv = []
            aggregation = 0
            for agent in self.agents:
                if voting_power[agent.id-1][idx] != 0:
                    error[idx] += voting_power[agent.id-1][idx] * agent.error[idx]
                    aggregation += voting_power[agent.id-1][idx]

                    div.append(agent)
                    wdiv.extend([agent for i in range(int(voting_power[agent.id-1][idx]))])

            error[idx] = error[idx] / aggregation

            diversity[idx] = calc_population_diversity(div)
            weighted_diversity[idx] = calc_population_diversity(wdiv)

            votes_left[idx] = float(aggregation)/self.amount*100

        if self.PRINT:
            print('Error percentages')
            print(error)
            print('Div_vote')
            print(diversity)
            print('WDiv_vote')
            print(weighted_diversity)
            print('Votes_left_%' )
            print(votes_left)

        return (error, diversity, weighted_diversity, votes_left)

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
                print('total agents in sample: ' + str(self.amount))
                print(agent.id, agent.links)
                quit("ERROR: THIS AGENT HAS NO LINKS")

    def search_best_links(self, epsilon):
        ### LIQUID VERSION, searches agent.links for highest agent.link.ability
        if DEBUG:
            print('searching for best links of agents')

        for agent in self.agents:                   # For each agent
            #agent.best_links = []
            x = np.empty([0,len(agent.ability)])    # x is ability of links
            for link in agent.links:                # for each link of agent
                for agent2 in self.agents:          # all other agents
                    if link == agent2.id:           # if other agent is a link
                        ab = agent2.ability
                        for i in range(len(ab)):
                            ab[i] = ab[i] + uniform(-epsilon, epsilon)  # ability is changed with epsilon
                        x = np.vstack([x, ab])      # x is stacked ability
            agent.best_links = [agent.links[i] for i in np.argmax(x, axis=0)] # argmax calcs best abilities in x, list comprehension gives the best_link ids
            #print(agent.best_links)

    def delegation(self):
        voting_power = np.ones([len(self.agents), self.subjects])  ## voting power of agent, 1 per agent/subject
        received_from = [[[] for _ in range(self.subjects)] for _ in range(self.amount)]
        DELEGATE = True
        while DELEGATE:
            print('NEW DELEGATION ROUND')
            DELEGATE = False
            for agent in self.agents:                               # For each agent
                for idx in range(self.subjects):                    # for each subject
                    if voting_power[agent.id][idx] != 0:            # if agent has voting power
                        if agent.best_links[idx] != agent.id:       # if agent wants to delegate
                            if agent.best_links[idx] in received_from[agent.id][idx]: # Agent wants to delegate to agent that it received power from, so CIRCLE DETECTED
                                if DEBUG:
                                    print('Delegation cycle detected in landscape ' + str(idx) + ', deleting number of votes: ' + str(len(received_from[agent.id][idx])))
                                voting_power[agent.id][idx] = 0 # voting power set to 0, no delegation
                                # THIS MAY BE CHANGED FOR EXPERIMENTATIONS
                            else:
                                print(str(agent.id) + ' is delegating...')
                                print('best option = ' + str(agent.best_links[idx]))
                                print('received from = ' + str(received_from[agent.id][idx]))
                                print(agent.best_links[idx] in received_from[agent.id][idx])
                                DELEGATE = True
                                deleg = voting_power[agent.id][idx] # how much power is delegated
                                voting_power[agent.id][idx] = 0     # own voting power set to 0
                                voting_power[agent.best_links[idx]][idx] += deleg   # voting power of delegate is updated

                                if agent.id not in received_from[agent.best_links[idx]][idx]:
                                    received_from[agent.best_links[idx]][idx].append(agent.id) # Add agent.id to best link received votes
        if DEBUG:
            print("DELEGATION done")
        return voting_power