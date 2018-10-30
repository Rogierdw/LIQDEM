import sys, csv
from World import World

SWEEP = False

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

    (d, d_e, d_d) = world.direct()
    (r1, r1_e, r1_d) = world.representative_abil(degree)
    (r2, r2_e, r2_d) = world.representative_rand(degree)

    (l1, l1_e, l1_d, l1_wd) = world.liquid('random', degree, epsilon)
    (l2, l2_e, l2_d, l2_wd) = world.liquid('regular', degree, epsilon)
    (l3, l3_e, l3_d, l3_wd) = world.liquid('ring', degree, epsilon)
    (l4, l4_e, l4_d, l4_wd) = world.liquid('small', degree, epsilon)
    (l5, l5_e, l5_d, l5_wd) = world.liquid('scale free', degree, epsilon)
    (l, l_e, l_d, l_wd) = world.liquid('fully', epsilon=epsilon)

    row1 = d.tolist() + r1.tolist() + r2.tolist() + l1.tolist() + l2.tolist() + l3.tolist() + l4.tolist() + \
           l5.tolist() + l.tolist()
    row2 = d_e.tolist() + r1_e.tolist() + r2_e.tolist() + l1_e.tolist() + l2_e.tolist() + l3_e.tolist() + \
           l4_e.tolist() + l5_e.tolist() + l_e.tolist()
    row3 = [d_d] + [r1_d] + [r2_d] + l1_d.tolist() + l2_d.tolist() + l3_d.tolist() + \
           l4_d.tolist() + l5_d.tolist() + l_d.tolist()
    row4 = [d_d] + [r1_d] + [r2_d] + l1_wd.tolist() + l2_wd.tolist() + l3_wd.tolist() + \
           l4_wd.tolist() + l5_wd.tolist() + l_wd.tolist()
    return (row1, row2, row3, row4)

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
    degree = 20
    percentage = 100
    epsilon = 0.02
    iterations = 100

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
                         'p_' + str(epsilon) + 'e' + '.csv', 'w', newline='') as h:
                writer1 = csv.writer(f)
                writer2 = csv.writer(g)
                writer3 = csv.writer(h)

                writer1.writerow(['direct']*subjects + ['rep_ability']*subjects + ['rep_random']*subjects +
                                ['liq_random']*subjects + ['liq_regular']*subjects + ['liq_ring']*subjects +
                                ['liq_small']*subjects + ['liq_scalefree']*subjects + ['liq_full']*subjects)

                writer2.writerow(['direct'] + ['rep_ability'] + ['rep_random'] +
                                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects + ['liq_full'] * subjects)

                writer3.writerow(['direct'] + ['rep_ability'] + ['rep_random'] +
                                 ['liq_random'] * subjects + ['liq_regular'] * subjects + ['liq_ring'] * subjects +
                                 ['liq_small'] * subjects + ['liq_scalefree'] * subjects + ['liq_full'] * subjects)


                for i in range(iterations):
                    print('ROUND: '+ str(degree) +', ITERATION: ' + str(i+1))
                    (res, err, div, wdiv) = sweep(subjects=subjects, degree = degree, percentage = percentage, epsilon=epsilon)
                    writer1.writerow(err)
                    writer2.writerow(div)
                    writer3.writerow(wdiv)
    else:
        single(subjects=subjects, degree = degree, percentage = percentage, epsilon=epsilon)



    '''
    if(len(sys.argv)<=1):
        main()
    else:
        main(subjects = int(sys.argv[1]), size = int(sys.argv[2]))
    '''