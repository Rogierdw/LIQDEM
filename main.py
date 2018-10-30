import sys, csv
from World import World

SWEEP = False
EPSWEEP = True

def old_main_1(subjects = 2, size = 1000, min = 1, max = 100, smoothing = 3):
    world = World(subjects, size, min, max, smoothing)
    # print(world.world)

    world.direct()

    #world.liquid('fully')

    world.liquid('random')
    world.liquid('regular')
    world.liquid('small')
    world.liquid('power')

def sweep(subjects = 5, size = 2000, min = 1, max = 100, degree = 20, percentage = 100, epsilon = 0):
    world = World(subjects, size, min, max, percentage, PRINT=False)
    # print(world.world)

    (d_e, d_d) = world.direct()
    (r1_e, r1_d) = world.representative_abil(degree)
    (r2_e, r2_d) = world.representative_rand(degree)

    (l1_e, l1_d, l1_wd, l1_v) = world.liquid('random', degree, epsilon)
    (l2_e, l2_d, l2_wd, l2_v) = world.liquid('regular', degree, epsilon)
    (l3_e, l3_d, l3_wd, l3_v) = world.liquid('ring', degree, epsilon)
    (l4_e, l4_d, l4_wd, l4_v) = world.liquid('small', degree, epsilon)
    (l5_e, l5_d, l5_wd, l5_v) = world.liquid('scale free', degree, epsilon)
    #(l_e, l_d, l_wd, l_v) = world.liquid('fully', epsilon=epsilon)

    row2 = d_e.tolist() + r1_e.tolist() + r2_e.tolist() + l1_e.tolist() + l2_e.tolist() + l3_e.tolist() + \
           l4_e.tolist() + l5_e.tolist()# + l_e.tolist()
    row3 = [d_d] + [r1_d] + [r2_d] + l1_d.tolist() + l2_d.tolist() + l3_d.tolist() + \
           l4_d.tolist() + l5_d.tolist()# + l_d.tolist()
    row4 = [d_d] + [r1_d] + [r2_d] + l1_wd.tolist() + l2_wd.tolist() + l3_wd.tolist() + \
           l4_wd.tolist() + l5_wd.tolist()# + l_wd.tolist()
    row5 = [100] + [float(degree)/world.amount] + [float(degree)/world.amount] + l1_v.tolist() + l2_v.tolist() + l3_v.tolist() + \
           l4_v.tolist() + l5_v.tolist()# + l_v.tolist()
    return (row2, row3, row4, row5)

def single(subjects = 5, size = 2000, min = 1, max = 100, degree = 20, percentage = 100, epsilon = 0):
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

    subjects = 5
    degree = 10
    percentage = 100
    epsilons = [0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
    iterations = 10

    if SWEEP:
        for epsilon in epsilons:
        # TO CSV!
            with open('error_' + str(subjects) + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(percentage) +
                              'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as f,\
                    open('diversity_'+ str(subjects)
                            + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(percentage) +
                              'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as g,\
                    open('weight_diversity_' + str(subjects)
                         + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(percentage) +
                         'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as h, \
                    open('votes_left_percent_' + str(subjects)
                         + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(percentage) +
                         'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as x:
                writer1 = csv.writer(f)
                writer2 = csv.writer(g)
                writer3 = csv.writer(h)
                writer4 = csv.writer(x)

                writer1.writerow(['direct']*subjects + ['rep_ability']*subjects + ['rep_random']*subjects +
                                ['liq_random']*subjects + ['liq_regular']*subjects + ['liq_ring']*subjects +
                                ['liq_small']*subjects + ['liq_scalefree']*subjects)# + ['liq_full']*subjects)

                writer2.writerow(['direct'] + ['rep_ability'] + ['rep_random'] +
                                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)

                writer3.writerow(['direct'] + ['rep_ability'] + ['rep_random'] +
                                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)

                writer4.writerow(['direct'] + ['rep_ability'] + ['rep_random'] +
                                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)


                for i in range(iterations):
                    print('ROUND: '+ str(epsilon) +', ITERATION: ' + str(i+1))
                    (err, div, wdiv, vot) = sweep(subjects=subjects, degree = degree, percentage = percentage, epsilon=epsilon)
                    writer1.writerow(err)
                    writer2.writerow(div)
                    writer3.writerow(wdiv)
                    writer4.writerow(vot)
    elif EPSWEEP:
        for epsilon in epsilons:
            with open('votes_left_percent_' + str(subjects) + 's_' + str(iterations) + 'i_' + str(degree) + 'd_' + str(percentage) +
                              'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as f:
                writer4 = csv.writer(f)
                writer4.writerow(['direct'] + ['rep_ability'] + ['rep_random'] +
                                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects)# + ['liq_full'] * subjects)
                for i in range(iterations):
                    print('ROUND: '+ str(epsilon) +', ITERATION: ' + str(i+1))
                    (err, div, wdiv, vot) = sweep(subjects=subjects, degree = degree, percentage = percentage, epsilon=epsilon)
                    writer4.writerow(vot)
    else:
        single(subjects=subjects, degree = degree, percentage = percentage, epsilon=epsilon)
