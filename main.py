import hashlib
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from IPNetwork import IPNetwork
from Helper import Utility
from Pastry import PastryDHT
import os
import sys

def generateRandomString():
    charString = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([random.choice(charString) for i in range(10)])


class configuration():
    def __init__(self, initNodes, dataPoints, SearchQ, addNode=0, deleteNode=0):
        self.initNode, self.dataPoints, self.searchQ, self.addNode, self.deleteNode = initNodes, dataPoints, SearchQ, addNode, initNodes//2
        self.database = []
        self.histo = []

    def initPastry(self):
        print('Started Pastry Simulation With initial Nodes=', self.initNode)
        self.pastry = PastryDHT(self.initNode)

    def addDataToPastry(self):
        print('Adding data Points = ', self.dataPoints)
        for _ in range(self.dataPoints):
            key, value = Utility.convertToHexId(generateRandomString()), generateRandomString()
            self.pastry.addKey(key, value)
            self.database.append(key)

    def deleteFromPastry(self):
        print('Performing deletion of half nodes = ', self.deleteNode)
        for _ in range(self.deleteNode):
            self.pastry.deleteNode()
    
    def addNodesToPastry(self):
        pass

    def searchFromPastry(self):
        print('Performing random search Queries = ', self.searchQ)
        for _ in range(self.searchQ):
            randomKey = random.choice(self.database)
            hopeCount = self.pastry.findKey(randomKey)
            self.histo.append(hopeCount)
        print('Average Nums of Hope = ', sum(self.histo)/self.searchQ)
        print('Actual Hope', math.log(IPNetwork.totalNodeCount, 16))
    
    def saveHistograpm(self, name, prop):
        figFolder = os.path.join(os.getcwd(), 'fig') 
        f = plt.figure()
        plt.hist(self.histo, bins = 50)
        if prop == 1:
            titleString = "Distribution Histogram of Hop: Total Pastry Nodes "+ str(self.initNode)
        else:
            titleString = "Distribution Histogram of Hop: Total Pastry Nodes After Deleting 50% rendom Node" + str(self.deleteNode)

        plt.title(titleString)
        plt.xlabel("Hop Count")
        plt.ylabel("Number of Search Queries")
        filename = os.path.join(figFolder, name + '.pdf')
        f.savefig(filename, bbox_inches='tight')
        self.histo.clear()
    def statistics(self):
        self.pastry.statistics()

    def simulation(self):
        print('***********************Start Simulation ****************************')
        self.initPastry()
        self.addDataToPastry()
        self.searchFromPastry()
        self.saveHistograpm(str(self.initNode) + '_Before Deletion', 1)
        self.deleteFromPastry()
        self.searchFromPastry()
        self.saveHistograpm(str(self.initNode) + '_After Deletion', 2)
        # self.statistics()
        print('*************************End Simulation ********************')

if __name__ == "__main__":
    # f = open('output.txt','w'); sys.stdout = f
    c1 = configuration(100,  10000, 1000000)
    c2 = configuration(500,  10000, 1000000)
    c3 = configuration(1000, 10000, 1000000)
    
    c1.simulation()
    c2.simulation()
    c3.simulation()
