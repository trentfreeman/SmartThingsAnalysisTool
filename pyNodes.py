import re
import copy
import itertools

                

#DONT FORGET: give app init array of single app (starting with --app-start--)
###############   NODE CODE  #####################################################
class app:
    def __init__(self,string):
        self.name = string[1].split(' ')[1]
        #TODO: DO I NEED SEPERATE DEVICE STATE ARRAY OR ADD TO STATE ARRAY
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
                arr = re.findall(r'this.subscribe\(.*\)', line)
                print(arr)
                for item in arr:
                    x= start(item[item.index('(')+1:-1].split(','), string, self)
                    print(x)
                    self.startNodes += [x]
        
    def asString(self):
        string = 'Application ' +self.name + '\nStarts: ['
        string += '\n'.join([x.asString()+'\n' for x in self.startNodes])
        string += ']'
        return string

    def __repr__(self):
        return self.asString()

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
        self.tree = self.createTree(text.split(': ')[1], self, app)

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
        if 'state.' in self.left.lower() or 'atomicstate.' in self.left.lower():
            self.hasState = True
            if not(self.left in app.StateVar):
                app.StateVar += [self.left]
        if len(arr)>1:
            self.right = arr[1].strip('[]() ')
            if 'state.' in self.right.lower() or 'atomicstate.' in self.right.lower():
                self.hasState = True
                if not(self.right in app.StateVar):
                    app.StateVar += [self.right]
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
        return self.asString()

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
    def __init__(self, path, starts):
        #for item in path array is a tuple of indicies that indicate where the first path nodes are in the interleaving.
        self.path1Placements = path[0]
        self.pathInter = path[1:]
        self.starts = starts

    def racePossible(self):
        racePossible = False
        tup = self.path1Placements
        #if a path is using state variables
        isUsingStateArr = [False,False]
        if (tup[0] == len(self.pathInter) - len(tup) or tup[0] == 0) and sequenceInOrder(tup):
            return False
        else:
            itemPathNum = None
            for item in self.pathInter:
                if self.pathInter.index(item) in tup:
                    itemPathNum = 1
                    tup = tup[1:]
                else:
                    itemPathNum = 2
                classType = item.__class__.__name__
                if classType == 'expresNode':
                    if item.hasState and 'state' in item.left:
                        if (itemPathNum == 1 and isUsingStateArr[1] == True) or (itemPathNum == 2 and isUsingStateArr[0]):
                            return True
                        isUsingStateArr[itemPathNum-1] = True
            return False

    def startsSequences(self):
        sequenceStates = []
        for item in self.pathInter:
            classType = item.__class__.__name__
            if classType == 'expresNode' and item.deviceExpres:
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
    #for textArr[0] in textArr:
    if re.findall(r'\[if|^(,\[if)', textArr[0], flags = re.IGNORECASE): 
        arr = splitCommas(textArr[0])
        x = ifNode(arr, method, app, textArr[1:])
        return x
        #retNodes += x
    elif re.findall(r'\[\(|^(,\[\()', textArr[0], flags = re.IGNORECASE):
        arr = textArr[0].split('=')
        if len(arr) == 2:
            x = expresNode(arr, method, app, textArr[1:])
            return x
        #    retNodes += x
        else:
            print("I don't know how to categorize: " + textArr[0])
            return
    elif bool([x for x in app.deviceStates if x.attr in textArr[0]]):
        device = [x for x in app.deviceStates if x.attr in textArr[0]][0]
        print(textArr[0])
        arr = re.findall(re.escape(device.attr)+'\w*\.\w*', textArr[0], flags = re.IGNORECASE)
        for cmd in device.commands:
            if cmd in textArr[0]:
                arr += [cmd]
                break
        print(arr)
        x = expresNode(arr,method,app,textArr[1:], True)
        return x
    else:
        print("I don't know how to categorize: " + textArr[0])
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
                print(item)
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
