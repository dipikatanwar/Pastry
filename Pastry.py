import hashlib
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from Node import Node
from IPNetwork import IPNetwork
from Helper import Utility


class PastryDHT():
    def __init__(self, numberOfNode, b = 4):
        IPNetwork.init()
        self.b, self.M, self.L, self.LBY2 = b, int(math.pow(2,b+1)),int(math.pow(2,b)),int(math.pow(2,b)/2)
        self.totalDataInsert, self.insertQueryCount, self.deleteQueryCount, self.uniqueId = 0, 0, 0, 0
        self.totalDataAddQ, self.totalDataSearchQ, self.totalNodeInsertQ, self.totalNodeDelQ = 0,0,0,0
        self.generateNodes(numberOfNode)

    def generateNodes(self, N):
        for _ in range(N):
        #     self.addNode()
            nodeId,geoLocation = Utility.convertToHexId(self.uniqueId), Utility.randomLocation()
            node = Node(nodeId,geoLocation)
            IPNetwork.nodeInfo[nodeId] = node
            IPNetwork.totalNodeCount += 1
            self.uniqueId += 1 
        self.makeOverlayNetwork()

    def makeOverlayNetwork(self):
        nodeList = list(IPNetwork.nodeInfo.values())
        for indexI in range(IPNetwork.totalNodeCount):
            geoDistance, idDistanceLeft, idDistanceRight, i = [],[],[], nodeList[indexI]
            for indexJ in range(IPNetwork.totalNodeCount):
                if indexI == indexJ: continue
                j = nodeList[indexJ]
                dist = Utility.distanceInIdSpace(j.nodeId,i.nodeId)
                if dist > 0:
                    idDistanceRight.append((j,dist))
                else:
                    idDistanceLeft.append((j,abs(dist)))
                geoDistance.append((j,Utility.euclidianDistance(i.geoLocation, j.geoLocation)))
                preFix = Utility.prefixMatch(i.nodeId, j.nodeId)
                next1 = int(j.nodeId[preFix],16)
                ele = i.routingTable[preFix][next1]
                if not ele or Utility.absDistanceInIdSpace(ele.nodeId,i.nodeId) > Utility.absDistanceInIdSpace(j.nodeId,i.nodeId):
                    i.routingTable[preFix][next1] = j

            idDistanceLeft = sorted(idDistanceLeft, key = lambda x:x[1])[:self.LBY2]
            idDistanceRight = sorted(idDistanceRight, key = lambda x: x[1])[:self.LBY2]
            geoDistance = sorted(geoDistance, key = lambda x: x[1])[:self.M]

            i.lowerLeafSet = [itr[0] for itr in idDistanceLeft][::-1]
            i.upperLeafSet = [itr[0] for itr in idDistanceRight]
            i.neighbourHoodSet =[itr[0] for itr in geoDistance]

        


    def addKey(self,key,value):
        self.totalDataAddQ += 1
        seedNode = IPNetwork.getSeedNode()
        node, hopeCount, path = seedNode.addKey(key,value)
        if node: return node
        return None

    def findKey(self,key):
        self.totalDataSearchQ += 1
        seedNode = IPNetwork.getSeedNode()
        _, hopeCount, path = seedNode.findKey(key)
        return hopeCount

    def addNode(self):
        self.totalNodeInsertQ += 1
        global LOG
        # LOG = True
        nodeId, geoLocation = Utility.convertToHexId(self.uniqueId),Utility.randomLocation()
        self.uniqueId += 1
        newNode = Node(nodeId,geoLocation)
        # Find a node near by in geographic space, Assume it is seed node
        startNode = IPNetwork.findNearest(newNode)
        if not startNode:
            IPNetwork.nodeInfo[newNode.nodeId] = newNode
            IPNetwork.totalNodeCount += 1
            return

        nearestNode,hopeCount, path = startNode.route(newNode.nodeId)
        newNode.neighbourHoodSet = Utility.sortedInsertGeo(newNode, startNode.neighbourHoodSet, startNode)[:self.M]

        if Utility.distanceInIdSpace(newNode.nodeId, nearestNode.nodeId) > 0:
            newNode.upperLeafSet = nearestNode.upperLeafSet.copy()
            newNode.lowerLeafSet = nearestNode.lowerLeafSet.copy() + [nearestNode]
            newNode.lowerLeafSet = newNode.lowerLeafSet[-self.LBY2:]
        else:
            newNode.lowerLeafSet = nearestNode.lowerLeafSet.copy()
            newNode.upperLeafSet = [nearestNode] + nearestNode.upperLeafSet.copy()
            newNode.upperLeafSet = newNode.upperLeafSet[:self.LBY2]

        for nodeL in newNode.lowerLeafSet:
            nodeL.upperLeafSet = Utility.sortedInsert(nodeL.upperLeafSet, newNode)[:self.LBY2]
        
        for nodeR in newNode.upperLeafSet:
            nodeR.lowerLeafSet = Utility.sortedInsert(nodeR.lowerLeafSet, newNode)[-self.LBY2:]


        for node in path:
            preFix = Utility.prefixMatch(node.nodeId, newNode.nodeId)
            for i in range(preFix+1):
                for j in range(len(newNode.routingTable[i])):
                    if not node.routingTable[i][j]: continue
                    ele = newNode.routingTable[i][j]
                    if not ele or Utility.absDistanceInIdSpace(newNode.nodeId, node.routingTable[i][j].nodeId) < Utility.absDistanceInIdSpace(ele.nodeId, newNode.nodeId):
                        newNode.routingTable[i][j] = node.routingTable[i][j]

            next1 = int(node.nodeId[preFix],16)
            ele = newNode.routingTable[preFix][next1]

            if not ele or Utility.absDistanceInIdSpace(newNode.nodeId, node.nodeId) < Utility.absDistanceInIdSpace(ele.nodeId, newNode.nodeId):
                newNode.routingTable[preFix][next1] = node
        IPNetwork.joinInNetwork(newNode)

        IPNetwork.nodeInfo[newNode.nodeId] = newNode
        IPNetwork.totalNodeCount += 1


    def deleteNode(self):
        self.totalNodeDelQ += 1
        FailedRandomNode = IPNetwork.getSeedNode()
        backUpdata = FailedRandomNode.data
        
        for nodeL in FailedRandomNode.lowerLeafSet:
            try:
                nodeL.upperLeafSet.remove(FailedRandomNode)
                if nodeL.upperLeafSet[-1] and len(nodeL.upperLeafSet[-1].upperLeafSet) !=0:
                    nodeL.upperLeafSet = nodeL.upperLeafSet + nodeL.upperLeafSet[-1].upperLeafSet
                nodeL.upperLeafSet = nodeL.upperLeafSet[:self.LBY2]
            except Exception as e:
                pass
                # print('Left ', e)
        
        try:
            for nodeR in FailedRandomNode.upperLeafSet:
                nodeR.lowerLeafSet.remove(FailedRandomNode)
                if nodeR.lowerLeafSet[0] and len(nodeR.lowerLeafSet[0].lowerLeafSet)!=0:
                    nodeR.lowerLeafSet =  nodeR.lowerLeafSet[0].lowerLeafSet + nodeR.lowerLeafSet 
                nodeR.lowerLeafSet = nodeR.lowerLeafSet[-self.LBY2:]
        except Exception as e:
            pass
            # print('right ', e)
        
        for nodeId, node in IPNetwork.nodeInfo.items():
            if FailedRandomNode in node.neighbourHoodSet:node.neighbourHoodSet.remove(FailedRandomNode)
            if nodeId == FailedRandomNode.nodeId:continue
            preFix = Utility.prefixMatch(FailedRandomNode.nodeId, nodeId)
            next1 = int(nodeId[preFix],16)
            if node.routingTable[preFix][next1] and node.routingTable[preFix][next1].nodeId == FailedRandomNode.nodeId:
                node.routingTable[preFix][next1] = None
                for k in range(preFix, len(node.routingTable)):
                    for q in range(len(node.routingTable[k])):
                        if q == next1: continue
                        nextNode = node.routingTable[k][q]
                        if nextNode and nextNode.routingTable[preFix][next1] and Utility.prefixMatch(nextNode.nodeId, nodeId)==preFix:
                            node.routingTable[preFix][next1] = nextNode.routingTable[preFix][next1]


        del IPNetwork.nodeInfo[FailedRandomNode.nodeId]
        IPNetwork.totalNodeCount -=1

        for k, v in backUpdata.items():self.addKey(k,v)
    
    def statistics(self):
        print("Total number of nodes :", IPNetwork.totalNodeCount)
        print("Total number of data elements :", self.totalDataAddQ)
        print("Total number of search :", self.totalDataSearchQ)
        # print("Total number Node Add Query :", self.totalNodeInsertQ)
        print("Total number None Del Query:", self.totalNodeDelQ)
        self.printNode(IPNetwork.getSeedNode().nodeId)

    def printNode(self,nodeId):
        node = IPNetwork.nodeInfo[nodeId]
        print("Routing Table Of ", nodeId)
        print()
        print(['S.N. | ', 'Successor'])
        for sn, row in enumerate(node.routingTable):
            entry = [x.nodeId for x in row if x]
            print(sn," | ",entry)
