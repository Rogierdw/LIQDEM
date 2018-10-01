import sys
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

    world.direct()
    world.representative(degree)

    world.liquid('fully')

    world.liquid('random', degree)
    world.liquid('regular', degree)
    world.liquid('ring', degree)
    world.liquid('small', degree)
    world.liquid('scale free', degree)




if __name__ == '__main__':
    print(sys.version)

    if(len(sys.argv)<=1):
        main()
    else:
        main(subjects = int(sys.argv[1]), size = int(sys.argv[2]))