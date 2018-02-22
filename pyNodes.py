class app:
    def __init__(self,stringArr):
        inMethods = False
        self.methodArr = []
        self.startNodes = []
        count = 0
        for line in stringArr:
            if 'Starting Points:' in line:
                inMethods = False
                break
            if "processing" in line and not(inMethods):
                self.name = line[11:]
            if "DECLARED METHODS" in line:
                inMethods = True
            if inMethods == True: 
                if ':' in line:
                    newLine = line.split(':')
                    self.methodArr.append(methNode(newLine[0], newLine[1], self))
    
    def __repr__(self):
        return 'Application ' +self.name + '; Starts: [' + ', '.join(map(repr,self.startNodes)) + ']; Methods: [' +(', ').join(map(repr, self.methodArr)) + ']'

class methNode:
    def __init__(self, name, methodText, parent):
        self.name = name
        self.parent = parent
        self.arrNextNodes = []
        textArr = splitBrack(methodText)
        for item in textArr:
            print(item)
            if len(item) > 5:
                if '[If' in item[0:4]: 
                    arr = splitCommas(item)
                    x = ifNode(arr, self.parent)
                    self.arrNextNodes.append(x)
                if '[(' in item[0:4]:
                    arr = item.split('=')
                    if len(arr) == 2:
                        x = expresNode(arr)
                        self.arrNextNodes.append(x)
                    else:
                        print("I don't know how to categorize: " + item)
            if 'subscribe' in item and not('unsubscribe' in item):
                print("I found a subscribe node")
                x= startNode(item, self.parent)
                self.arrNextNodes.append(x)

    def __repr__(self):
        return self.name + '[' + ', '.join(map(str, self.arrNextNodes)) + ']'

                    
class Node:
    def __init__(self,stringArr):
        self.stringArr = stringArr

    def parse(self, string):
        #TODO: WORK ON PARSING THE IF STATEMENTS/ MAKING GENERAL PARSER (FOR LOOPS, WHILE LOOPS, etc.)
        textArr = spliCommas(string)
        for item in textArr:
            print(item)
            if len(item) > 5:
                if '[If' in item[0:4]: 
                    arr = splitCommas(item)
                    x = ifNode(arr, self.parent)
                    self.arrNextNodes.append(x)
                if '[(' in item[0:4]:
                    arr = item.split('=')
                    if len(arr) == 2:
                        x = expresNode(arr)
                        self.arrNextNodes.append(x)
                    else:
                        print("I don't know how to categorize: " + item)
            if 'subscribe' in item and not('unsubscribe' in item):
                print("I found a subscribe node")
                x= startNode(item, self.parent)
                self.arrNextNodes.append(x)
        newString = splitBrack(string)
        print(newString)

class startNode(Node):
    def __init__(self, string, parent):
        print(string)
        args = string[:-2].split('(')[1].split(',')
        self.subTo = args[1].strip()
        self.callFunc = args[2].strip()
        self.parent = parent
        parent.startNodes += [self]

    def __repr__(self):
        return self.subTo +' calls--> '+ self.callFunc 

class expresNode:
    def __init__(self, arr):
        self.right = arr[0]
        self.left = arr[1]

    def __repr__(self):
        return self.right + ' = ' + self.left 

class conditionalState:
    def __init__(self):
        pass

class ifNode(Node):
    def __init__(self, ifArray, parent):
        self.parent = parent
        #TODO: ADD || to if state
        self.ifState = ifArray[0].strip().split('&&')
        self.trueBranch = self.parse(ifArray[1].strip())
        self.falseBranch = self.parse(ifArray[2].strip())

   def __repr__(self):
       #TODO can only be done after parsing
       print('I NEED TO PUT SOMETHING HERE')

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
        if left == right:
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
