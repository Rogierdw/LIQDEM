import sys, csv
from World import World

def old_main_1(subjects = 2, size = 1000, min = 1, max = 100, smoothing = 3):
    world = World(subjects, size, min, max, smoothing)
    # print(world.world)

    world.direct()

    #world.liquid('fully')

    world.liquid('random')
    world.liquid('regular')
    world.liquid('small')
    world.liquid('power')

def main(subjects = 5, size = 1000, min = 1, max = 100, degree = 20):
    world = World(subjects, size, min, max)
    # print(world.world)

    (d, d_e) = world.direct()
    (r1, r1_e) = world.representative_abil(degree)
    (r2, r2_e) = world.representative_rand(degree)

    #world.liquid('fully')

    (l1, l1_e) = world.liquid('random', degree)
    (l2, l2_e) = world.liquid('regular', degree)
    (l3, l3_e) = world.liquid('ring', degree)
    (l4, l4_e) = world.liquid('small', degree)
    (l5, l5_e) = world.liquid('scale free', degree)

    row1 = d.tolist() + r1.tolist() + r2.tolist() + l1.tolist() + l2.tolist() + l3.tolist() + l4.tolist() + l5.tolist()
    row2 = d_e.tolist() + r1_e.tolist() + r2_e.tolist() + l1_e.tolist() + l2_e.tolist() + l3_e.tolist() + l4_e.tolist() + l5_e.tolist()
    return (row1, row2)



if __name__ == '__main__':
    print(sys.version)

    subjects = 5
    iterations = 100
    degree = 60

    # TO CSV!
    with open('error'+str(iterations)+'_60.csv', 'w', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['direct']*subjects + ['rep_ability']*subjects + ['rep_random']*subjects +
                         ['liq_random']*subjects + ['liq_regukar']*subjects + ['liq_ring']*subjects +
                         ['liq_small']*subjects + ['liq_scalefree']*subjects)

        for i in range(iterations):
            print('ITERATION ' + str(i+1))
            (res, err) = main(subjects=subjects, degree = degree)
            writer.writerow(err)

    '''
    if(len(sys.argv)<=1):
        main()
    else:
        main(subjects = int(sys.argv[1]), size = int(sys.argv[2]))
    '''