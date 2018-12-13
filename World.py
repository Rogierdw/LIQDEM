from random import randint, uniform, shuffle, gauss
from scipy.stats import truncnorm as tn
from copy import copy
from Agent import Agent
import numpy as np
import networkx as nx
from operator import itemgetter
import itertools

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
    def __init__(self, subjects, size, mina, maxa, percentage, PRINT):
        self.PRINT = PRINT
        self.min = mina
        self.max = maxa
        self.subjects = subjects
        #OLD, SET SMOOTHING
        #self.world = [landscape(size,min,max,SF=3) for _ in range(subjects)]
        #NEW, Ramping smoothing
        self.world = []
        for SF in range(subjects):
            self.world.append(landscape(size=size, min=mina, max=maxa, SF = 2))
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

    def liquid(self, net_type, degree=15, epsilon=0):
        if self.PRINT:
            print('\nLIQUID DEMOCRACY')
            print('Network type = ' + net_type)
        self.create_network(net_type, degree)
        ## Each agent determines links with highest ability (best_links)
        self.search_best_links(epsilon=epsilon)

        if DEBUG:
            print('mean degree: ' + str(np.mean([len(agent.links) for agent in self.agents])))
            print('starting delegation of votes')

        ### Delegation in seperate function!
        delegtypes =  ["remove", "at_detect", "break_cycle", "cycle_subvote"]
        save = np.empty([0,8])

        i = 0
        for delegtype in delegtypes:
            (voting_power, cycle_results, cycle_theoretics, cycle_differences, cycle_diff_percentages) = self.delegation(epsilon=epsilon, delegtype=delegtype)


            ### Just result calculation from here
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
                    if voting_power[agent.id][idx] != 0:
                        error[idx] += voting_power[agent.id][idx] * agent.error[idx]
                        aggregation += voting_power[agent.id][idx]

                        div.append(agent)
                        wdiv.extend([agent for i in range(int(voting_power[agent.id][idx]))])

                error[idx] = error[idx] / aggregation

                diversity[idx] = calc_population_diversity(div)
                weighted_diversity[idx] = calc_population_diversity(wdiv)

                votes_left[idx] = float(aggregation)/self.amount

            if self.PRINT:
                print('Error percentages')
                print(error)
                print('Div_vote')
                print(diversity)
                print('WDiv_vote')
                print(weighted_diversity)
                print('Votes_left_%' )
                print(votes_left)

            add = np.concatenate((error, diversity, weighted_diversity, votes_left))
            add = np.append(add, [cycle_results, cycle_theoretics, cycle_differences, cycle_diff_percentages])

            save = np.vstack([save, add])
            #save.append([error.tolist(), diversity.tolist(), weighted_diversity.tolist(), votes_left.tolist(), cycle_results, cycle_theoretics, cycle_differences, cycle_diff_percentages])
        return save

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
                            #ab[i] = uniform(max(self.min,ab[i]-epsilon), min(self.max, ab[i]+epsilon)) # First bound, then take uniform sample of interval

                            ab[i] = gauss(ab[i], epsilon)  # Gauss

                            #ab[i] = tn.rvs(self.min-ab[i], self.max-ab[i], loc = ab[i], scale = epsilon) # truncated normal distribution

                            ab[i] = max(self.min,(min(ab[i], self.max))) # bound ability between min and max of landscape ## Extra check
                        x = np.vstack([x, ab])      # x is stacked ability
            agent.best_links = [agent.links[i] for i in np.argmax(x, axis=0)] # argmax calcs best abilities in x, list comprehension gives the best_link ids
            agent.best_original_links = agent.best_links.copy() # Keep list, best_links may change and need to revert to this
            agent.best_link_abils = np.max(x, axis=0)
            agent.best_original_link_abils = agent.best_link_abils.copy()
            #print(agent.best_links)

    def delegation(self, epsilon=0, delegtype="break_cycle"):
        ### REVERT agents.best_links[idx] to original, may change below for different cycle handlers

        for agent in self.agents:
            agent.best_links = agent.best_original_links.copy()

        voting_power = np.ones([self.amount, self.subjects])  ## voting power of agent, 1 per agent/subject
        received_from = [[[x] for _ in range(self.subjects)] for x in range(self.amount)]
        cycle_results = []
        cycle_theoretics = []
        cycle_differences = []
        cycle_diff_percentages = []
        DELEGATE = True
        while DELEGATE:
            #print('NEW DELEGATION ROUND')
            DELEGATE = False
            shuffle(self.agents)
            for idx in range(self.subjects):                        # for each subject
                for agent in self.agents:                           # For each agent
                    if voting_power[agent.id][idx] != 0:            # if agent has voting power
                        if agent.best_links[idx] != agent.id:       # if agent wants to delegate
                            if agent.best_links[idx] in received_from[agent.id][idx]: # Agent wants to delegate to agent that it received power from, so CIRCLE DETECTED
                                if DEBUG:
                                    print('Delegation cycle detected in landscape ' + str(
                                        idx) + ', handling number of votes: ' + str(len(received_from[agent.id][idx])))

                                cycle_list = received_from[agent.id][idx].copy()  ## Cycle with branches
                                actual_cycle = self.cycle_search(cycle_list, idx)  ## Only Cycle

                                if delegtype is "at_detect":
                                    agent.best_links[idx] = agent.id

                                if delegtype is "break_cycle":
                                    ## Extend Received list from current round!!
                                    ### This is important because voting power is set to 1 per agent. And because order is random setting could be done at a wring moment. Therefor the received_from list is first extended completely for the current round. So when voting power is set to 1 no agents are devoid of their voting power completely. This is only needed in this 'break_cycle' handling.
                                    extend = True
                                    while extend:
                                        extend = False
                                        for id in received_from[agent.id][idx]:
                                            for item in received_from[id][idx]:
                                                if item not in received_from[agent.id][idx]:
                                                    extend = True
                                                    received_from[agent.id][idx].append(item)

                                    cycle_list = received_from[agent.id][idx].copy()  ## Cycle with branches

                                    for id in cycle_list:
                                        received_from[id][idx] = [id]
                                        voting_power[id][idx] = 1

                                    actual_cycle = self.cycle_search(cycle_list, idx)
                                    for x in actual_cycle:
                                        for agent in self.agents:
                                            if agent.id == x:
                                                agent.best_links[idx] = agent.id

                                if delegtype is "cycle_subvote":
                                    self.cycle_decision(cycle_list=actual_cycle, epsilon=epsilon, idx=idx) # Seperate Function

                                if delegtype is "remove":
                                    voting_power[agent.id][idx] = 0
                                else:  # Cycle calculations done in all other cases
                                    abil = self.cycle_abil(searchlist=actual_cycle, idx=idx)
                                    theo = self.cycle_best_abil(searchlist=actual_cycle, idx=idx)
                                    # theo = self.cycle_theoretic_abil(searchlist=actual_cycle, idx=idx)*100 # Posibility calc
                                    diff = theo - abil
                                    diffper = diff * 100 / self.max
                                    cycle_results.append(abil)
                                    cycle_theoretics.append(theo)
                                    cycle_differences.append(diff)
                                    cycle_diff_percentages.append(diffper)

                            else:
                                DELEGATE = True
                                deleg = voting_power[agent.id][idx] # how much power is delegated
                                voting_power[agent.id][idx] = 0     # own voting power set to 0
                                voting_power[agent.best_links[idx]][idx] += deleg   # voting power of delegate is updated

                                received_from[agent.best_links[idx]][idx].append(agent.id) # Add agent.id to best link received votes
                                # Add receival branch elders
                                received_from[agent.best_links[idx]][idx] = list(set().union(received_from[agent.best_links[idx]][idx],received_from[agent.id][idx]))
                                #received_from[agent.best_links[idx]][idx].extend(received_from[agent.id][idx])

        cycle_results = None if len(cycle_results) is 0 else np.mean(cycle_results)
        cycle_theoretics = None if len(cycle_theoretics) is 0 else np.mean(cycle_theoretics)
        cycle_differences = None if len(cycle_differences) is 0 else np.mean(cycle_differences)
        cycle_diff_percentages = None if len(cycle_diff_percentages) is 0 else np.mean(cycle_diff_percentages)

        if DEBUG:
            print("DELEGATION done")

        return (voting_power, cycle_results, cycle_theoretics, cycle_differences, cycle_diff_percentages)

    def cycle_decision(self, cycle_list, epsilon, idx=0):
        maj_dict = {}
        for i in  cycle_list:
            maj_dict[i] = 0

        # All agents in cycle will define their delegate from that cycle AGAIN, so epsilon is redone!
        ## MAYBE want to remember what epsilon was if same candidate appears. Because it shouldn't have changed
        for agent in self.agents:
            if agent.id in cycle_list:
                agent.cycle_links = cycle_list
                x = np.empty(0)  # x is ability of links
                for link in agent.cycle_links:
                    for agent2 in self.agents:
                        if link == agent2.id:
                            if link == agent.best_links[idx]:
                                x = np.append(x, agent.best_link_abils[idx])
                            else:
                                ab = agent2.ability[idx]

                                #ab = uniform(max(self.min, ab - epsilon), min(self.max, ab + epsilon))
                                ab = gauss(ab, epsilon)
                                #ab = tn.rvs(self.min - ab, self.max - ab, loc=ab, scale=epsilon)

                                ab = max(self.min, (min(ab, self.max)))
                                x = np.append(x, ab)
                # argmax calcs best abilities in x, list comprehension gives the best_link ids
                maj_dict[agent.cycle_links[np.argmax(x, axis=0)]] += 1
                #agent.best_cycle_link = np.argmax(x, axis=0)
                #maj_dict[agent.best_cycle_link]+=1

        winner = max(maj_dict.items(), key=itemgetter(1))[0]
        for agent in self.agents:
            if agent.id == winner:
                agent.best_links[idx] = agent.id

    def cycle_search(self, searchlist, idx):
        best_links = {}
        for agent in self.agents:
            if agent.id in searchlist:
                best_links[agent.id] = [agent.best_links[idx]]

        def update(dictio):
            for x in dictio:
                dictio[x].append(dictio[dictio[x][-1]][0])

        def check(dictio):
            for x in dictio:
                if x in dictio[x]:
                    ### CYCLE DETECTED, all members of dictio[x] are in cycle
                    return True
            return False

        while not check(best_links):
            update(best_links)

        for x in best_links:        # x is key for all agent.id in circle + branches
            if x in best_links[x]:
                return best_links[x]

    def cycle_abil(self, searchlist, idx):
        abil = []
        for agent in self.agents:
            for id in searchlist:
                if agent.id is id:
                    if agent.best_links[idx] is agent.id:
                        abil.append(agent.ability[idx])
        return np.mean(abil)

    def cycle_theoretic_abil(self, searchlist, idx):
        maj = np.math.ceil((len(searchlist)+1)/2)
        abil = np.zeros(0)  ## Which ability comes from which agent is not needed, just the abilities
        for agent in self.agents:
            for id in searchlist:
                if agent.id is id:
                    abil = np.append(abil,agent.ability[idx])
        abil = abil/100
        result = 0

        # Calculations are done just with abil list
        while(maj <= len(searchlist)): # take all majority options even the one where everyone is correct
            pluss = list(itertools.combinations(abil,maj))
            for plus in pluss:
                plus = set(plus)
                min = [1 - x for x in list(set(abil) - plus)]
                plus = list(plus)
                result += np.prod(plus + min)
            maj +=1

        return result

    def cycle_best_abil(self, searchlist, idx):
        abil = np.zeros(0)
        for agent in self.agents:
            for id in searchlist:
                if agent.id is id:
                    abil = np.append(abil,agent.ability[idx])
        return np.max(abil)