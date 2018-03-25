import re
import copy
import itertools

                

#DONT FORGET: give app init array of single app (starting with --app-start--) (done in initializeString now)
###############   NODE CODE  #####################################################
class app:
    def __init__(self,string):
        self.name = string[1].split(' ')[1]
        #These must be at the top most level because they are global to the app
        self.StateVar = []
        self.deviceStates = self.findDevs(string)
        self.startNodes = []
        self.findStarts(string)
    
    def findDevs(self, string):
        deviceArr = []
        deviceLine = [x for x in string if "requested attrs:" in x][0][17:-1].split(', ')
        for device in deviceLine:
            x = deviceAttr(device)
            deviceArr += [x]
        return deviceArr


    def findStarts(self, string):
        arr = []
        for line in string:
            if 'this.subscribe' in  line:
                temp = re.findall(r'\[this.subscribe\(.*\)\]', line)
                arr = splitBrack(temp[0]) 
                for item in arr:
                    subArgs = re.findall(r'\(.*?\)', item)
                    subArgs = subArgs[0][1:-1].split(',')
                    x= start(subArgs, string, self)
                    self.startNodes += [x]
        
    def asString(self):
        string = 'Application ' +self.name + '\nStarts: ['
        string += '\n'.join([x.asString()+'\n' for x in self.startNodes])
        string += ']'
        return string

    def __repr__(self):
        return self.asString()

class stateVariable:
    def __init__(self, name, typeOf, critPoint = None):
        self.name = name
        self.typeOf = typeOf
        self.criticalPoints = []
        if typeOf != 'bool':
            self.addCritPoint(critPoint)

    def addCritPoint(self, point):
        if point != None:
            self.criticalPoints += [point] 
    
    def findCritPoint(self, ifStateArr):
        for item in ifStateArr:
            if self.name in item:
                #TODO
                return

    @staticmethod
    def determineType(expressNodeArr):
        arr = []
        indexState = -1
        for item in expressNodeArr:
            string = item.strip('()[] ')
            arr += [string]
            if 'state.' in string:
                indexState = arr.index(string)
        if 'now' in arr[(indexState+1)%2]:
            return 'num'
        else:
            return 'bool'

    def __repr__(self):
        return self.name
        

class deviceAttr:
    def __init__(self, attr):
        self.attr = attr
        self.commands = []
        f = open('Capabilities.csv', 'r')
        lines = f.read().split('\n')
        f.close()
        #because this is a well structured csv, I do this with no errors
        for x in lines:
            if 'capability.'+attr+',' in x:
                self.commands = x.split(',')[3].split(' ') 

class start:
    def __init__(self, arr, codeArr, app):
        self.app = app
        self.event = arr[0].strip()
        #TODO: get datatype from capfulll.csv
        #self.evtType = self.findDataType(arr[0].strip())
        for line in codeArr:
            stuff = re.findall(arr[2].strip() + ':', line, flags = re.IGNORECASE)
            if re.findall(arr[2].strip() + ':', line, flags = re.IGNORECASE):
                self.methodCall = method(arr[2].strip(), line, self.app)
                break
        
    def findDataType(self, cap):
        pass

    def asString(self):
        string = self.methodCall.asString()
        return string

    def __repr__(self):
        return self.asString()

class method:
    def __init__(self, name, text, app):
        self.name = name
        self.app = app
        self.variables = []
        #the join/split is to cut out the function name
        self.tree = self.createTree(': '.join(text.split(': ')[1:]), self, app)

    def createTree(self, text,method,app):
        textArr = splitBrack(text)

        return parse(textArr, method, app)

    def asString(self):
        string = ""
        if self.tree != None:
            string = self.name + ': \n' +self.tree.asString()
        return string

    def __repr__(self):
        return self.asString()


class baseNode():
    def __init__(self, method):
        self.nextNode = None
        self.method = method
        self.app = self.method.app

class expresNode(baseNode):
    def __init__(self, arr, method, app,text, deviceExpres = False):
        self.hasState = False
        self.deviceExpres = deviceExpres
        self.left = arr[0].strip('[]() ')
        inStateVar = False
        if 'state.' in self.left.lower() or 'atomicstate.' in self.left.lower():
            self.hasState = True
            for item in app.StateVar:
                if self.left in item.name:
                    inStateVar = True
            if not(inStateVar):
                varType = stateVariable.determineType(arr)
                x = stateVariable(self.left, varType)
                app.StateVar += [x]
        if len(arr)>1:
            self.right = arr[1].strip('[]() ')
            if 'state.' in self.right.lower() or 'atomicstate.' in self.right.lower():
                self.hasState = True
                for item in app.StateVar:
                    if self.left in item.name:
                        inStateVar = True
                if not(inStateVar):
                    varType = stateVariable.determineType(arr)
                    x = stateVariable(self.left, varType)
                    app.StateVar += [x]
        self.app = app
        self.method = method
        self.nextNode = parse(text, method, app) 

    def asString(self):
        string = ""
        if self.deviceExpres == True:
            string = '[('+self.left + ' -> ' + self.right+')]' 
        else:
            string = '[('+ self.left + ' = ' + self.right+')]'
        if self.nextNode != None:
            string += self.nextNode.asString()
        return string 

    def pathPrint(self):
        string = ""
        if self.deviceExpres == True:
            string = '[('+self.left + ' -> ' + self.right+')]' 
        else:
            string = '[('+ self.left + ' = ' + self.right+')]'
        return string


    def __repr__(self):
        return self.asString()


class ifNode(baseNode):
    def __init__(self, ifArray, method, app, text):
        self.app = app
        self.method = method
        self.ifBranch = ""
        #TODO: ELSE IFs
        self.trueBranch = None
        self.falseBranch = None
        #TODO: ADD || to if state
        self.ifState = ifArray[0].strip().split('&&')
        for item in app.StateVar:
            if [x for x in self.ifState if item.name in x] and item.typeOf != 'bool':
                item.findCritPoint(self.ifState)
        trueArr = splitBrack(ifArray[1].strip())
        self.trueBranch = parse(trueArr, self.method, self.app)
        if len(ifArray) >2:
            falseArr = splitBrack(ifArray[2].strip())
            self.falseBranch = parse(falseArr, self.method, self.app)
        if len(text)>0:
            self.nextNode = parse(text, self.method, self.app)

    def asString(self):
        string = '['+ ' && '.join(map(str,self.ifState)) + ' '
        if self.trueBranch != None:
            string += self.trueBranch.asString() 
        string += ', '
        if self.falseBranch != None:
            string += self.falseBranch.asString() 
        string += ']'
        if self.nextNode != None:
            string += self.nextNode.asString()
        return string 
    
    def pathPrint(self):
        string = '['+ ' && '.join(map(str,self.ifState)) + ']'
        return string

    def __repr__(self):
        return self.asString()

                


            
############# Path FUNCTIONS ###################################

class path:
    def __init__(self, startMeth, path = []):
        self.start = startMeth
        self.app = startMeth.app
        self.nodePath = path

    def asString(self):
        string = ""
        for item in self.nodePath:
            if item != None:
                string += item.__class__.__name__ +'\n'
        return string

    def __repr__(self):
        string = ""
        for item in self.nodePath:
            string += item.pathPrint()
        return string

class allPaths:
    def __init__(self, app):
        self.app = app
        self.paths = []
        self.allStarts = self.app.startNodes
        #This only does one startNode right now, a for loop would fix this
    
    def findPaths(self):
        for item in self.allStarts:
            self.findPathsRecurse(item, item.methodCall.tree)

    def findPathsRecurse(self, start, node = None, pathArr = []):
        nodeCurrent = node
        while nodeCurrent != None:
            nodeClass = nodeCurrent.__class__.__name__
            pathArr += [nodeCurrent]
            if nodeClass == "expresNode":
                nodeCurrent = nodeCurrent.nextNode
            elif nodeClass == "ifNode":
                if nodeCurrent.trueBranch != None:
                    self.findPathsRecurse(start, nodeCurrent.trueBranch, copy.copy(pathArr))
                if nodeCurrent.falseBranch != None:
                    self.findPathsRecurse(start, nodeCurrent.falseBranch, copy.copy(pathArr))
                nodeCurrent = nodeCurrent.nextNode
        self.paths += [path(start, pathArr)]

                

############# Comparison FUNCTIONS ###################################
class compareInterPathStarts:
    def __init__(self, paths, starts):
        #for item in path array is a tuple of indicies that indicate where the first path nodes are in the interleaving.
        self.allInterleavings = paths
        self.starts = starts
        self.allPathCombos = None
        self.interleave =None

    def runTest(self):
        nodeUsedArr = []
        outputRaceArr = []
        retArr = []
        self.allPathCombos = list(itertools.combinations_with_replacement(paths.paths, 2))
        print(self.allPathCombos)
        for start in self.starts:
            for item in self.allPathCombos:
                self.interleave = interleavings(item[0].nodePath, item[1].nodePath)
                for inter in self.interleave:
                    outputRaceArr += [self.getResultPath(inter)]
                nodeUsedArr.append([item[0], item[1], outputRaceArr]) 
                outputRaceArr = []
            retArr.append([start, nodeUsedArr]) 
            nodeUsedArr = []
        return retArr


    def getResultPath(self, path):
        tup = path[0]
        pathInter = path[1:]
        path2NodesLeft = len(pathInter) - len(tup)
        retVal = False
        sequenceStates = []
        path1Final = None
        path2Final = None
        racePossible = False
        #if a path is using state variables
        isUsingStateArr = [False,False]
        itemPathNum = None
        for item in pathInter:
            #get the sequence of state changes as they happen
            classType = item.__class__.__name__
            if classType == 'expresNode' and item.deviceExpres:
                if pathInter.index(item) in tup:
                    path1Final = [item.left+'->'+item.right]
                else:
                    path2Final = [item.left+'->'+item.right]
                sequenceStates += [item.left +'->'+item.right]
            #determine if race possible
            if pathInter.index(item) in tup:
                itemPathNum = 1
                tup = tup[1:]
                if len(tup) == 0:
                    isUsingStateArr[0] = False
            else:
                path2NodesLeft -=1
                if path2NodesLeft == 0:
                    isUsingStateArr[1] =False
                itemPathNum = 2

            classType = item.__class__.__name__
            if classType == 'expresNode':
                if item.hasState and 'state' in item.left:
                    if (itemPathNum == 1 and isUsingStateArr[1] == True) or (itemPathNum == 2 and isUsingStateArr[0]):
                        retVal = True
                    isUsingStateArr[itemPathNum-1] = True
        return {'path1Order': path[0], 'racePossible': retVal, 'path1State': path1Final, 'path2State': path2Final, 'sequenceStates': sequenceStates}

    def startsSequences(self):
        sequenceStates = []
        for item in self.pathInter:
            classType = item.__class__.__name__
            if classType == 'expresNode' and item.deviceExpres:
                if self.pathInter.index(item) in self.path1Placements:
                    self.path1FinalState = [item.left+'->'+item.right]
                else:
                    self.path2FinalState = [item.left+'->'+item.right]
                sequenceStates += [item.left +'->'+item.right]
        return sequenceStates



            
############# Helper FUNCTIONS #################################
def splitBrack(string):
    left = 0
    right = 0
    retArr = []
    lastSplit = 0
    for i in range(0, len(string)):
        if string[i] == '[':
            left +=1
        if string[i] == ']':
            right +=1
        if left == right and left !=0:
            retStr= string[lastSplit:i+1]
            lastSplit = i+1
            retArr.append(retStr)
    return retArr


def splitCommas(string):
    left=1
    right=0
    retArr = []
    lastSplit = 1
    for i in range(1,len(string)-1):
        if string[i] == '[':
            left +=1
            right -=1
        if string[i] == ']':
            right +=1
            left -=1
        if left == 1 and right == 0 and string[i] == ',':
            retStr = string[lastSplit:i+1]
            lastSplit = i +1
            retArr.append(retStr)
    return retArr



def parse(textArr, method, app):
    #TODO: WORK ON PARSING THE IF STATEMENTS/ MAKING GENERAL PARSER (FOR LOOPS, WHILE LOOPS, etc.)
    try:
        if re.findall(r'\[if|^(,\[if)', textArr[0], flags = re.IGNORECASE): 
            arr = splitCommas(textArr[0])
            x = ifNode(arr, method, app, textArr[1:])
            return x
        #TODO: MAKE EXPRESNODE CASE FOR lights?.on() case in hall-light*.groovy
        elif re.findall(r'\[\(|^(,\[\()', textArr[0], flags = re.IGNORECASE):
            arr = textArr[0].split('=')
            if len(arr) == 2:
                x = expresNode(arr, method, app, textArr[1:])
                return x
            else:
                print("I don't know how to categorize: " + textArr[0])
                return
        elif bool([x for x in app.deviceStates if x.attr in textArr[0]]):
            device = [x for x in app.deviceStates if x.attr in textArr[0]][0]
            arr = re.findall(re.escape(device.attr)+'\w*\.\w*', textArr[0], flags = re.IGNORECASE)
            for cmd in device.commands:
                if cmd in textArr[0]:
                    arr += [cmd]
                    break
            x = expresNode(arr,method,app,textArr[1:], True)
            return x
        else:
            print("I don't know how to categorize: " + textArr[0])
            return
    except IndexError:
        print("Index Orror in parse: textArr = ", end = '')
        print(textArr)
        return


def initializeString(fileName):
    f= open(fileName,'r')
    string = f.read()
    f.close()
    #fix for multiple apps
    string = string.lower()
    stringArr = string.split('\n')
    methods = stringArr[stringArr.index('declared methods') +1:stringArr.index('starting points: []')]
    #code below is to replace method calls within methods with their text (very annoying)
    """
    for line in methods:
        matches =[x.lower() for x in methods if x.split(': ')[0].lower() in line.split(': ')[1].lower()]
        methodSplit = splitBrack(line.lower().split(': ')[1])
        for match in matches:
            for text in methodSplit:
                #if "this.subscribe" in text:
                    #break
                if match.split(': ')[0] in text:
                    #TEST THIS WITH DIFFERENT OUTPUT, DOESN'T WORK WITH c02 MONITOR BECAUSE NO METHODCALLS WITHIN METHODS
                    #On second thought i dont know if this works the way i want it to. surprise surprise
                    methodSplit[methodSplit.index(text)] = re.sub(re.escape(match.split(': ')[0]) + '\(.*\)', match.split(': ')[1], text, flags=re.IGNORECASE)
        methods[methods.index(line)] = line.split(': ')[0] + ': ' + ''.join(methodSplit)
    """
    stringArr[stringArr.index('declared methods') +1:stringArr.index('starting points: []')] = methods
    return stringArr


def getAllBoolLists(arr, num):
    if num == 0:
        return [arr]
    else:
        arrT = getAllBoolLists(arr+[True], num-1)
        arrF = getAllBoolLists(arr+[False], num-1)
        return arrT +arrF


#startVars are assumed to only be Bools
def getAllPossibleStarts(app):
    allStarts = []
    stateStarts = []
    arrArrBools = getAllBoolLists([], len(app.StateVar))
    for arrBools in arrArrBools:
        dictState = {}
        for i in range(0,len(arrBools)):
            dictState[app.StateVar[i]] = arrBools[i]
        stateStarts += [dictState]
    deviceState = {}
    deviceStarts = []
    for device in app.deviceStates:
        if deviceStarts == []:
            for item in device.commands:
                deviceState[device.attr] = item
                deviceStarts += [deviceState.copy()]
        else:
            deviceStartsCP = deviceStarts.copy()
            for item in deviceStartsCP:
                for command in device.commands:
                    item[device.attr] = command
                    deviceStarts += [item]
            #remove dupes
    if stateStarts ==[]:
        allStarts = deviceStarts
    else:
        for item in stateStarts:
            for device in deviceStarts:
                for k in device:
                    item[k] =device[k] 
                    print(item)
                    allStarts += [item.copy()]
    return allStarts

#taken and adapted from https://stackoverflow.com/questions/15306231/how-to-calculate-all-interleavings-of-two-lists
def interleavings(path1, path2):
    allInter = []
    singleInter = [None]*(len(path1) +len(path2))
    for combo in itertools.combinations(range(0,len(singleInter)), len(path1)):
        singleInter = [None]*(len(path1) +len(path2))
        index1 = 0
        index2 = 0
        for item in combo:
            singleInter[item] = path1[index1]
            index1+=1
        for i in range(0,len(singleInter)):
            if singleInter[i] == None:
                singleInter[i] = path2[index2]
                index2+=1
        singleInter = [combo] +singleInter
        allInter.append(singleInter)
    return allInter

def sequenceInOrder(tup):
    lastItem = None
    for item in tup:
        if lastItem == None:
            lastItem = item
        else:
            if item-lastItem != 1:
                return False
    return True

                

                


#STARTING HERE
#TODO: MAKE THIS READ FROM overprivout.txt (THIS IS A FINAL THING)            
#MAKE TREE HERE
stringArr = initializeString('testing.txt')
testApp = app(stringArr)
paths = allPaths(testApp)
paths.findPaths()
starts = getAllPossibleStarts(testApp)
testInter = compareInterPathStarts(paths, starts)
results = testInter.runTest()
# RESULT DESCRIPTION
# x is variable to change, z is an arbitrary number
# first level = results[x]: array of [startVariableArray, all results associated with start] DON'T USE: LARGE OUTPUT
# second = results[y][x]: access either startVariable Array with results[0][0] (SMALL OUTPUT) or the results with results[0][1] (LARGE OUTPUT)
# third = results[y][1][x]: array of paths interleaved, and the results for the paths [path1, path2, resultsWithAllInterleavings] (DONT USE LARGE OUTPUT)
# fourth = results[z][1][0][0 or 1]: path1 (index 0) or path2 (index 1)
# fourth = results[z][1][0][2] = array of dictionaries with the result of a specific interleaving of the paths from above with the start at the second level
# fifth = results[z][1][0][2][x]: individual results (a lot of work to get here, could definitely be organized better)

#EXPLAINING BELOW: 
#Output is in the following closed form
#First two lines label the start currently being examined
#next two lines give the two paths being examined for results below
# next two lines are atomic result from path1 first then path 2 first
# total races counted in all of the interleavings
# final two lines are the number of times the sequence of state changes in the interleavings matched the atomic interleaving sequence.

# This isnt clean right now, but it gets my results. 
for start in results:
    print("START")
    print(start[0])
    for paths2 in start[1]:
        countSameAsAtomic12 = 0 
        countSameAsAtomic21 = 0 
        countRaces = 0 
        print("PATH 1: ", end = "")
        print(paths2[0])
        print("PATH 2: ", end = "")
        print(paths2[1])
        p1p2Atomic = paths2[2][0]
        print(p1p2Atomic)
        p2p1Atomic = paths2[2][-1]
        print(p2p1Atomic)
        for result in paths2[2][1:-1]:
            if p1p2Atomic['path1State'] == result['path1State']:
                #it has the same final state in path1 as in interleaved(IS ALWAYS TRUE FOR STATE)
                pass
            if p2p1Atomic['path2State'] == result['path2State']:
                #it has the same final state in path2 as in interleaved(IS ALWAYS TRUE FOR STATE)
                pass
            if p1p2Atomic['sequenceStates'] == result['sequenceStates']:
                countSameAsAtomic12 +=1
            if p2p1Atomic['sequenceStates'] == result['sequenceStates']:
                countSameAsAtomic21 +=1
            if result['racePossible']:
                countRaces +=1
        print("COUNT RACES: ", end = "")
        print(countRaces)
        print("COUNT STATE CHANGE SAME AS p1->p2 ATOMIC: ", end = "")
        print(countSameAsAtomic12)
        print("COUNT STATE CHANGE SAME AS p1->p2 ATOMIC: ", end = "")
        print(countSameAsAtomic21)
