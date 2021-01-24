import math, time

#A class which is used to store the information for each node in the list#
class Node():

    def __init__(self, position = None, parent = None):

        self.position = position
        self.parent = parent

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

#The actual Pathfinding algorithm#
def aStar(gameboard, startNode, endNode):
    #Sets up placeholders for varibles#
    walls = []
    closedSet = []
    openSet = []

    #Adds the positions of each wall to the list#
    for x in range(0, len(gameboard[0])-1):
        for y in range(0, len(gameboard[0])):
            if gameboard[y][x] == "#":
                walls.append((x,y))

    #Appends the inital node to the open set of nodes#
    openSet.append(startNode)

    #Goes through every node untill the openset is empty or the end node is found#
    while openSet != []:
        #sets current node and index to that of the first node in the open set#
        currentNode = openSet[0]
        currentIndex = 0

        #Goes throught the open set, if the node value f is less then that of current node set the new current node to that node and change it to that index#
        for index, node in enumerate(openSet):
            if node.f < currentNode.f:
                currentNode = node
                currentIndex = index

        #Moves the current node to the closed set and removes itself from the open one#
        openSet.pop(currentIndex)
        closedSet.append(currentNode)

        #Ends the loop and returns the movement path if the current node is the same as the end node#
        if currentNode.position == endNode.position:
            path = []
            current = currentNode
            while current is not None:
                path.append(current.position)
                current = current.parent

            rePath = path[::-1]
            movement = []
            
            for i in range (len(rePath)-1):
                movement.append(((rePath[i+1][0] - rePath[i][0]),(rePath[i+1][1] - rePath[i][1])))

            return movement

        #Creates an empty list to contain the current nodes children then loops through all the nodes possible children#
        children = []
        for newPosition in [(0, -1), (0, 1), (-1, 0), (1, 0)]:

            nodePosition = (currentNode.position[0] + newPosition[0], currentNode.position[1] + newPosition[1])

            #Prevents nodes from being added to list if they are note on the board or are actually wall tiles#
            if (nodePosition[0] > len(gameboard[0])) or (nodePosition[1] > len(gameboard)) or (nodePosition[0] < 0) or (nodePosition[1] < 0):
                continue

            if nodePosition in walls:
                continue

            #Creates a new node for the child and appends it the list of children#
            newNode = Node(nodePosition, currentNode)
            children.append(newNode)

        #List throught the children that are valid and calculates there g, h and f values#
        for child in children:

            #Doesn't create data for child if they are already in the closed set#
            if child in closedSet:
                continue
            
            child.g = currentNode.g + 1
            
            dx1 = abs(child.position[0] - endNode.position[0])
            dy1 = abs(child.position[1] - endNode.position[1])

            child.h = dx1**2 + dy1**2
            child.f = (child.g**2) + child.h

            #Removes from openset if is already in the open set#
            found = False
            for openNode in openSet:
                if child == openNode:
                    if child.g >= openNode.g:
                        found = True
                        continue

                    else:
                        openSet.remove(openNode)

            #Appends the the child to the open set if it isn't already there#
            if found == False:
                openSet.append(child)
