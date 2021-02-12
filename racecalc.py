import math
import matplotlib.pyplot as plt
import sys
import getopt


def load():
    #Get power tuples
    power = []
    with open("power.lut", "r") as file:
        line = file.readline()
        while line:
            s = line.split("|")
            s = s[0:len(s)]
            power.append((int(s[0]), int(s[1])))
            line = file.readline()

    #Load gear
    gear = [
        2.5, 1.875, 1.529, 1.2777, 1.105, 1
    ]

    #Load final
    final = 3.6

    #Load radius
    radius = 0.32

    #Calculate ratios
    ratios = []
    for i in gear:
        ratios.append((((1000/60)/i)/final)*radius*2*math.pi*3.6)

    #Make the matrix(table)
    table = []
    for ratio in ratios:
        val = []
        for p in power:
            val.append((p[0]*ratio/1000, p[1]/ratio))
        table.append(val)
    speeds = []
    for i, g in enumerate(table):
        for j, tup in enumerate(g):
            if j+1 < len(g) and i+1 < len(table):
                nexttup = g[j+1]
                nextgear = table[i+1]
                for count, x in enumerate(nextgear):
                    if round(tup[0], 2) <= x[0] <= round(nexttup[0], 2):
                        # check torque
                        if round(tup[1], 2) > round(nexttup[1], 2) and round(nexttup[1], 2) <= round(x[1], 2) <= round(tup[1], 2):
                            prev = nextgear[count-1]
                            #next gear points
                            x1, y1 = x
                            x2, y2 = prev
                            m1 = (y2-y1)/(x2-x1)
                            b1 = y1 - m1*x1

                            #curr gear points
                            x1, y1 = tup
                            x2, y2 = nexttup
                            m2 = (y2-y1)/(x2-x1)
                            b2 = y1 - m2*x1

                            #combine
                            total = (b1-b2)/(m2-m1)
                            #debug
                            #print(f"found {x}")
                            #print(f"calculated: {total}")
                            speeds.append(total)
    return (power, gear, final, radius, table, ratios, speeds)


#debug
#print(power)
#print(ratios)
#print(table)
#print(speeds)

#Plotting
def plot(table):
    for g in table:
        plt.plot(*zip(*g))
    plt.show()


def main(argv):
    (power, gear, final, radius, table, ratios, speeds) = load()
    for i, speed in enumerate(speeds):
        print(f"Gear {i}: {speed}")
    print("Inputs used: (use this to verify the load)")
    print(f"Gears: {gear}\nFinal: {final}\nRadius: {radius}")
    plot(table)


main(True)
