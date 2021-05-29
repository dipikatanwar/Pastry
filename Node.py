import hashlib
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from Helper import Utility
MAX_HOPE = 50
LOG = False

class Node():
    def __init__(self, id, geoLocation, b=4):
        self.b, self.M, self.L, self.LBY2 = b, int(math.pow(2,b+1)),int(math.pow(2,b)),int(math.pow(2,b)/2)
        self.nodeId, self.geoLocation, self.data = id, geoLocation,{}
        self.neighbourHoodSet, self.upperLeafSet, self.lowerLeafSet = [],[],[]
        self.routingTable = Utility.initializeRountingTable(128//self.b, int(math.pow(2,self.b)))

    def findNearestIn(self, key, nodeList):
        nearest = nodeList[0]
        dist = Utility.absDistanceInIdSpace(nodeList[0].nodeId, key)
        for i in range(1, len(nodeList)):
            dist1 = Utility.absDistanceInIdSpace(nodeList[i].nodeId, key)
            if dist > dist1:
                nearest = nodeList[i]
                dist = dist1
        return nearest

    def isInLeaf(self,key):
        keyToInet = Utility.hexToDec(key)
        searchSet = self.lowerLeafSet + self.upperLeafSet
        if len(searchSet) == 0:return False, None
        if Utility.hexToDec(searchSet[0].nodeId) <= keyToInet and Utility.hexToDec(searchSet[-1].nodeId) >= keyToInet:
            return True, self.findNearestIn(key, searchSet)
        return False, None


    def route(self,key, hopeCount=0):
        global LOG, MAX_HOPE
        if hopeCount >= MAX_HOPE: return None, 0, []
        distanceFromCurrNode = Utility.absDistanceInIdSpace(self.nodeId, key)
        # if LOG:print(self.nodeId, " ", distanceFromCurrNode)
        if distanceFromCurrNode ==0: return self,0,[self]
        ret, leafNode = self.isInLeaf(key)
        if ret:
            if distanceFromCurrNode < Utility.absDistanceInIdSpace(key,leafNode.nodeId):
                return self,0,[self]
            if LOG: print('in leaf ', leafNode.nodeId)
            node, hopeCount, path = leafNode.route(key, hopeCount+1)
            return node, hopeCount + 1, [self]+ path
        # if LOG: print('not in leaf')
        preFix = Utility.prefixMatch(key, self.nodeId)
        next1 = int(key[preFix],16)
        nextNode = self.routingTable[preFix][next1]
        if nextNode and distanceFromCurrNode < Utility.absDistanceInIdSpace(key, nextNode.nodeId):
            nextNode = None
        if LOG and nextNode: print('in routing ', nextNode.nodeId)
        flag = False
        if not nextNode:
            searchSet = self.lowerLeafSet + self.upperLeafSet + self.neighbourHoodSet
            for i in self.routingTable:searchSet.extend(i)
            for node in searchSet:
                if node and (Utility.prefixMatch(key, node.nodeId) >= preFix) and (distanceFromCurrNode > Utility.absDistanceInIdSpace(key, node.nodeId)):
                    flag = True
                    nextNode = node
                    distanceFromCurrNode = Utility.absDistanceInIdSpace(key, node.nodeId)
        if not nextNode: return self, 0, [self]
        if LOG and nextNode and flag: print('other ', nextNode.nodeId)
        node, hopeCount, path = nextNode.route(key, hopeCount+1)
        return node, hopeCount+1, [self] + path

    def addKey(self,key, value):
        node, hopeCount, path = self.route(key, 0)
        if node:node.data[key] = value
        return node,hopeCount, path

    def findKey(self,key):
        node, hopeCount, _ = self.route(key, 0)
        if node and key in node.data.keys():
            return True,hopeCount, node.data[key]
        return False, hopeCount, None
