import hashlib
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from Helper import Utility
class IPNetwork():
    nodeInfo = {}
    totalNodeCount = 0

    def init():
        IPNetwork.nodeInfo = {}
        IPNetwork.totalNodeCount = 0

    def findNearest(givenNode):
        init = False
        nearestNode = None
        for nodeId, node in IPNetwork.nodeInfo.items():
            dist = Utility.euclidianDistance(givenNode.geoLocation, node.geoLocation)
            if not init or dist1 > dist:
                nearestNode = node
                dist1 = dist
                init = True
        return nearestNode

    def findNearestInId(key):
        init = False
        nearestNode = None
        for nodeId, node in IPNetwork.nodeInfo.items():
            dist = Utility.absDistanceInIdSpace(key, node.nodeId)
            if not init or dist1 > dist:
                nearestNode = node
                dist1 = dist
                init = True
        return nearestNode

    def reDistributeKeys(srcNode,destNode):
        srcData = {}
        for k,v in srcNode.data.items():
            if Utility.absDistanceInIdSpace(k,srcNode.nodeId) > Utility.absDistanceInIdSpace(k,destNode.nodeId):
                destNode.data[k] = v
            else:
                srcData[k] = v
        srcNode.data = srcData.copy()

    def joinInNetwork(newNode):
        for nodeId, node in IPNetwork.nodeInfo.items():
            node.neighbourHoodSet =Utility.sortedInsertGeo(node,node.neighbourHoodSet, newNode)[:newNode.M]
            preFix = Utility.prefixMatch(newNode.nodeId, nodeId)
            next1 = int(newNode.nodeId[preFix],16)
            elem = node.routingTable[preFix][next1]
            if not elem or Utility.absDistanceInIdSpace(elem.nodeId, nodeId) > Utility.absDistanceInIdSpace(newNode.nodeId, nodeId):
                node.routingTable[preFix][next1] = newNode
            IPNetwork.reDistributeKeys(node, newNode)

    def getSeedNode():
        return random.choice(list(IPNetwork.nodeInfo.values()))