def bubbleSortPowerUps(inputList):
    
    outputList = inputList.copy()
    listSorted = False
    
    while listSorted == False:
        listSorted = True
        
        for i in range(len(outputList) - 1):
            if outputList[i+1][1] < outputList[i][1]:
                placeholder = outputList[i]
                outputList[i] = outputList[i+1]
                outputList[i+1] = placeholder
                listSorted = False

    return outputList
