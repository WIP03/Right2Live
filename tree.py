class skillTree():

    #Initalises the tree#
    def __init__(self):
        self.nodes = {'0': ["No Skill Selected", True, '-1', ["Please select a skill to view", "is effects or unlock with points."] ]}
        self.size = 1

    #Used to print all current nodes in the tree#
    def printNodes(self):
        for i in self.nodes:
            print(self.nodes[str(i)])
        print()

    #Used to add nodes to the list if there parent exists#
    def addNodes(self, name, parent, description):
        
        if parent in self.nodes:
            self.nodes[str(self.size)] = [name, False, parent, description]
            self.size += 1
            
        else:
            print("parent doesn't exist cant add node")

    #Removes a node from the list if they exists removing any children they have aswell#       
    def removeNodes (self, node, recursion):
        
        newTree = []
        recursion = recursion
        
        if node in self.nodes:
            newTree.append(node)
            
            for i in range(len(self.nodes)):
                if self.nodes[i][2] == node:
                    recursion += 1
                    newTree = newTree + self.removeNodes(i, recursion)
                    recursion -= 1
            
        else:
            print("node doesn't exist cant remove")
        
        
        if recursion != 0:
            return newTree
        
        else:
            for i in newTree:
                self.size -= 1
                del self.nodes[i]
                
            return self.nodes

    #Used to unlock a skill if is parrent is unlocked#    
    def unlockSkill(self, node):
                 
        for i in range(len(self.nodes)):
            if (self.nodes[node][2] == str(i)):
                if (self.nodes[str(i)][1] == True):
                    self.nodes[node][1] = True
            

#OLD TESTING CODE KEPT JUST INCASE IS NEEDED#    
#tree = skillTree()

#Node Name, parent node number, description of node function#
#tree.addNodes("Extra Points", 0, ["Gives player +100", "starting points", "each game."])

#tree.addNodes("Health One",1, ["Gives the player", "+5 health at the", "start of game."])
#tree.addNodes("Health Two",2, ["Increase the rate", "at which a player", "heals by 2%."])
#tree.addNodes("Health Three",3, ["Medpouch pickups", "give the player", "an extra +5 health."])
#tree.addNodes("Health Four",3, ["Gives the player", "+5 health at the", "start of game."])

#tree.addNodes("Speed One",1, ["Gives the player", "a speed increase", "of 5% each game."])
#tree.addNodes("Speed Two",6, ["Increase the rate", "of weapon fire", "by 2%."])
#tree.addNodes("Speed Three",7, ["Increase length", "of the speed", "upgrade by 2 seconds."])
#tree.addNodes("Speed Four",7, ["Gives the player", "a speed increase", "of 5% each game."])

#tree.addNodes("Heavy One",1, ["Decrease the time", "to reload a weapon", "by 5%."])
#tree.addNodes("Heavy Two",10, ["Increase the damage", "a player deals", "by 2%."])
#tree.addNodes("Heavy Three",11, ["Increase length", "of the double", "damage by 2 seconds."])
#tree.addNodes("Heavy Four",11, ["Decrease the time", "to reload a weapon", "by 5%."])

#tree.printNodes()
