import hashlib
import random
import math
import matplotlib.pyplot as plt
import numpy as np

class Utility():
    def convertToHexId(id):
        hashCode = hashlib.md5(str(id).encode()).hexdigest()
        return hashCode

    def max(l1,l2):
        if l1 >= l2:
            return l1
        return l2

    def min(l1,l2):
        if l1 < l2:
            return l1
        return l2

    def distanceInIdSpace(hex1, hex2):
        return int(hex1,16) - int(hex2,16)

    def absDistanceInIdSpace(hex1,hex2):
        return abs(Utility.distanceInIdSpace(hex1,hex2))

    def euclidianDistance(geoLocation1, geoLocation2):
        return np.linalg.norm(np.array(geoLocation1) - np.array(geoLocation2))

    def randomLocation():
        return (random.choice(range(90)), random.choice(range(180)))

    def prefixMatch(hex1,hex2):
        hex1,hex2, count = list(str(hex1)), list(str(hex2)),0
        for i in range(len(hex1)):
            if hex1[i] != hex2[i]:
                break
            else:
                count += 1
        return count

    def hexToDec(hex):
        return int(hex, 16)

    def sortedInsert(nodeList, newNode):
        if len(nodeList) ==0 : return [newNode]
        for i in range(len(nodeList)):
            if Utility.hexToDec(nodeList[i].nodeId) > Utility.hexToDec(newNode.nodeId):break
        return nodeList[:i] + [newNode] + nodeList[i:]
    
    def sortedInsertGeo(rootNode, nodeList, newNode):
        if len(nodeList) ==0 : return [newNode]
        rootNodeGeo = rootNode.geoLocation
        ele = newNode.geoLocation
        for i in range(len(nodeList)):
            if Utility.euclidianDistance(rootNodeGeo, nodeList[i].geoLocation) > Utility.euclidianDistance(rootNodeGeo,ele):break
        return nodeList[:i] + [newNode] + nodeList[i:]

    def initializeRountingTable(row,col):
        return [[None for i in range(col)] for j in range(row)]