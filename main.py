import sys, csv
from World import World
from time import time
from numpy import linspace, append

SWEEP = True

def old_main_1(subjects = 2, size = 1000, min = 1, max = 100, smoothing = 3):
    world = World(subjects, size, min, max, smoothing)
    # print(world.world)

    world.direct()

    #world.liquid('fully')

    world.liquid('random')
    world.liquid('regular')
    world.liquid('small')
    world.liquid('power')

def sweep(subjects = 1, size = 2000, min = 1, max = 100, degree = 15, percentage = 75, epsilon = 0):
    world = World(subjects, size, min, max, percentage, PRINT=False)
    # print(world.world)

    (d_e, d_d) = world.direct()
    #(r1_e, r1_d) = world.representative_abil(degree)
    #(r2_e, r2_d) = world.representative_rand(degree)

    l1_save = world.liquid('random', degree, epsilon)
    print(l1_save)
    quit()

    l2_save = world.liquid('regular', degree, epsilon)
    l3_save = world.liquid('ring', degree, epsilon)
    l4_save = world.liquid('small', degree, epsilon)
    l5_save = world.liquid('scale free', degree, epsilon)
    #(l_e, l_d, l_wd, l_v) = world.liquid('fully', epsilon=epsilon)

    err = d_e + l1_e + l2_e + l3_e +  l4_e + l5_e
    div = [d_d] + l1_d + l2_d + l3_d + l4_d + l5_d
    wdiv = [d_d] + l1_wd + l2_wd + l3_wd + l4_wd + l5_wd
    vot = [100] + l1_v + l2_v + l3_v + l4_v + l5_v


    return (err, div, wdiv, vot)

def single(subjects = 5, size = 2000, min = 1, max = 100, degree = 15, percentage = 75, epsilon = 0):
    world = World(subjects, size, min, max, percentage, PRINT=True)
    # print(world.world)

    #world.direct()
    #world.representative_abil(degree)
    #world.representative_rand(degree)

    world.liquid('random', degree, epsilon)
    world.liquid('regular', degree, epsilon)
    world.liquid('ring', degree, epsilon)
    world.liquid('small', degree, epsilon)
    world.liquid('scale free', degree, epsilon)
    world.liquid('fully', degree, epsilon)

if __name__ == '__main__':
    print(sys.version)

    subjects = 1
    degree = 15
    iterations = 100
    name = 'Cycle_Investigation_complete'

    percentages = [50/13.2, 250/13.2, 500/13.2, 1000/13.2]

    #e = linspace(0,1,11)
    #e2 = linspace(1.5,10,18)
    #epsilons = append(e,e2)

    epsilons = linspace(0.5,5,10)

    if SWEEP:
        for percentage in percentages:
            for epsilon in epsilons:
                ### FILESNAMES
                with open(name + '_error_' + str(subjects) + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(int(percentage*13.2)) +
                                  'pop_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as f,\
                        open(name + '_diversity_'+ str(subjects)
                                + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(int(percentage*13.2)) +
                                  'pop_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as g,\
                        open(name + '_weight_diversity_' + str(subjects)
                             + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(int(percentage*13.2)) +
                             'pop_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as h:#, \
                        #open(name + '_votes_left_percent_' + str(subjects)
                        #     + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(int(percentage*13.2)) +
                        #     'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as x:
                    writer1 = csv.writer(f)
                    writer2 = csv.writer(g)
                    writer3 = csv.writer(h)
                    #writer4 = csv.writer(x)

                    ### COLUMN HEADERS
                    writer1.writerow(['direct']*subjects +
                                    ['liq_random']*subjects + ['liq_regular']*subjects + ['liq_ring']*subjects +
                                    ['liq_small']*subjects + ['liq_scalefree']*subjects)# + ['liq_full']*subjects)['rep_ability']*subjects + ['rep_random']*subjects +

                    writer2.writerow(['direct'] +
                                     ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                     ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)['rep_ability'] + ['rep_random'] +

                    writer3.writerow(['direct'] +
                                     ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                     ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)['rep_ability'] + ['rep_random'] +

                    #writer4.writerow(['direct'] +
                    #                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                    #                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)['rep_ability'] + ['rep_random'] +

                    ### ACTUAL ITERATIONS
                    for i in range(iterations):
                        print("Percentage: "+ str(percentage) + ', Epsilon: '+ str(epsilon) +', ITERATION: ' + str(i+1))
                        (err, div, wdiv, vot) = sweep(subjects=subjects, degree = degree, percentage = percentage, epsilon=epsilon)
                        writer1.writerow(err)
                        writer2.writerow(div)
                        writer3.writerow(wdiv)
                        #writer4.writerow(vot)

    else:
        single(subjects=subjects, degree = degree, percentage = percentages[-1], epsilon=epsilons[0])
