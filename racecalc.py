import sys
import subprocess
import pkg_resources
import os

required = {'matplotlib', 'PyQt5'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    msstr = " ".join(missing)
    python = sys.executable
    os.system(f"{python} -m pip install {msstr}")

import math
import matplotlib.pyplot as plt
import getopt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class TableView(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def setData(self):
        horHeaders = []
        for n, key in enumerate(sorted(self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)


def load():
    #Get power tuples
    power = []
    with open("power.lut", "r") as file:
        line = file.readline()
        while line:
            if line != "\n" and line != "":
                s = line.strip().split("|")
                power.append((int(s[0]), int(s[1])))
            line = file.readline()

    #Load gear / final
    gear = []
    final = 0.0
    with open("drivetrain.ini", "r") as file:
        line = file.readline()
        while line:
            if "GEAR_" in line and "GEAR_R" not in line:
                gear.append(
                    float("".join([s for s in line[7:] if s in "0123456789."])))
            if "FINAL" in line:
                final = float(
                    "".join([s for s in line[6:] if s in "0123456789."]))
            line = file.readline()
    #Load radius
    radius = 0.0
    with open("tyres.ini", "r") as file:
        line = file.readline()
        while line:
            if "RADIUS=" in line[0:8]:
                radius = float(
                    "".join([s for s in line[7:] if s in "0123456789."]))
            line = file.readline()

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
                        if (round(tup[1], 2) > round(nexttup[1], 2) and round(nexttup[1], 2) <= round(x[1], 2) <= round(tup[1], 2)) or (round(nexttup[1], 2) > round(tup[1], 2) and round(tup[1], 2) <= round(x[1], 2) <= round(nexttup[1], 2)):
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
                            #print(f"{i} found {x}")
                            #print(f"calculated: {total}")
                            speeds.append(total)
    return (power, gear, final, radius, table, ratios, speeds)


def up(speeds, ratios):
    res = []
    for i, x in enumerate(speeds):
        res.append(x/ratios[i]*1000)
    return res


def down(speeds, ratios):
    res = []
    for i in range(1, len(speeds)+1):
        res.append(speeds[i-1]/ratios[i]*1000)
    return res

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
    plotb = False
    try:
        opts, args = getopt.getopt(argv, "hp")
    except getopt.GetoptError:
        print('Wrong Input')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            #help
            print(
                "Assetto Corsa Gear Change Calculator:\n  Args\n    -p  Will plot the data\n    -h  Shows this")
            sys.exit()
        elif opt in ("-p", "--plot"):
            plotb = True

    (power, gear, final, radius, table, ratios, speeds) = load()
    uprpm = up(speeds, ratios)
    downrpm = [0] + down(speeds, ratios)
    #debug
    #print("Gear | Kph    | Down    | Up")
    data = {"a.Gear": [], "b.Kph": [], "c.Down": [], "d.Up": []}

    for i, speed in enumerate(speeds):
        data["a.Gear"].append(str(i+1))
        data["b.Kph"].append(str(round(speed, 2)))
        data["c.Down"].append(str(int(round(downrpm[i], -2))))
        data["d.Up"].append(str(int(round(uprpm[i], -2))))

    #   debug    
    #   print(
    #       f"{i+1}    | {round(speed,2)} |    {int(round(downrpm[i], -2))} | {int(round(uprpm[i], -2))}")

    #print("Inputs used: (use this to verify the load)")
    #print(f"Gears: {gear}\nFinal: {final}\nRadius: {radius}")
    app = QApplication([])
    t = TableView(data, len(data["a.Gear"]), 4)
    win = QWidget()
    button = QPushButton("Plot")
    button.clicked.connect(lambda: plot(table))
    vbox = QVBoxLayout()
    vbox.addWidget(t)
    vbox.addStretch()
    vbox.addWidget(button)
    win.setLayout(vbox)

    win.setWindowTitle("Gear Change Calculator")
    win.show()
    app.exec()

if __name__ == "__main__":
   main(sys.argv[1:])
