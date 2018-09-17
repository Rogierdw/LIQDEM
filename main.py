import sys
from World import World

def main(subjects = 1, size = 2000, min = 1, max = 100, smoothing = 3, net_type = 'small'):
    output = World(subjects, size, min, max, smoothing, net_type)
    #print(output.world)



if __name__ == '__main__':
    print(sys.version)


    if(len(sys.argv)<=1):
        main()
    else:
        main(subjects = int(sys.argv[1]), size = int(sys.argv[2]), smoothing = int(sys.argv[3]))