import re

#TODO: DONT FORGET REPR METHODS
class app:
    def __init__(self,string):
        self.StateVar = []
        self.startNodes = findStarts(string)

    def findStarts(self, string):
        arr = []
        for line in string:
            if 'this.subscribe' in  line:
                arr = re.finall(r'this.subscribe\(.*\)', line)
                for item in arr:
                    x= start(item[item.index('(')+1:-1].split(','), text, self)
                    self.startNodes += x
        
    def __repr__(self):
        return 'Application ' +self.name + '; Starts: [' + ', '.join(map(repr,self.startNodes)) + ']' 

class start:
    def __init__(self, arr, codeArr, app):
        self.app = app
        self.event = arr[0].strip()
        #TODO: get datatype from capfulll.csv
        self.evtType = findDataType(arr[0].strip())
        for line in codeArr:
            if arr[1].strip() +':' in line:
                self.methodCall = method(arr[1].strip(), line, self.app)
                break
        
        def findDataType(self, cap):
            pass


class method:
    def __init__(self, name, text, app):
        self.name = name
        self.app = app
        self.variables = []
        self.Tree = Node(text, self)




#TODO: ALL BELOW
class Node:
    def __init__(self, name, methodText, app):
        #is this needed?
        return parse()
                
    def parse(self, string):
        #TODO: WORK ON PARSING THE IF STATEMENTS/ MAKING GENERAL PARSER (FOR LOOPS, WHILE LOOPS, etc.)
        textArr = splitBrack(string)
        for item in textArr:
            if len(item) > 5:
                if '[If' in item[0:4]: 
                    arr = splitCommas(item)
                    x = ifNode(arr, self.parent)
                    self.arrNextNodes.append(x)
                if '[(' in item[0:4]:
                    arr = item.split('=')
                    if len(arr) == 2:
                        x = expresNode(arr, self.parent)
                        self.arrNextNodes.append(x)
                    else:
                        print("I don't know how to categorize: " + item)
            if 'subscribe' in item and not('unsubscribe' in item):
                x= startNode(item, self.parent)
                self.arrNextNodes.append(x)


class methNode(Node):
    def __init__(self, name, methodText, app):
        self.name = name
        self.parent = parent
        self.arrNextNodes = []
        self.parse(methodText)

    def __repr__(self):
        return self.name + '[' + ', '.join(map(repr, self.arrNextNodes)) + ']'

                    
class startNode(Node):
    def __init__(self, string, parentApp, methodNode):
        args = string[:-2].split('(')[1].split(',')
        self.subTo = args[1].strip()
        self.callFunc = args[2].strip()
        self.parent = parent
        parent.startNodes += [self]
        self.methodNode = methodNode

    def __repr__(self):
        return self.subTo +' calls--> '+ self.callFunc 


class expresNode:
    def __init__(self, arr, parentApp, methodNode):
        self.right = arr[0]
        self.left = arr[1]
        self.parent = parentApp
        self.methodNode

    def __repr__(self):
        return self.right + ' = ' + self.left 


class ifNode(Node):
    def __init__(self, ifArray, parentApp, methodNode):
        self.parent = parent
        #TODO: ADD || to if state
        self.ifState = ifArray[0].strip().split('&&')
        self.trueBranch = Node(ifArray[1].strip(), self.parent)
        self.falseBranch = Node(ifArray[2].strip(), self.parent)
        self.parentApp = parentApp
        self.methodNode = methodNode

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


#TODO: ADD PREPROCESSING TO REPLACE METHOD CALLS WITH METHOD TEXT
#STARTING HERE
#TODO: MAKE THIS READ FROM overprivout.txt (THIS IS A FINAL THING)
f= open('testing.txt','r')
string = f.read()
f.close()
#fix for multiple apps
stringArr = string.split('\n')
methods = stringArr[stringArr.index('DECLARED METHODS') +1:stringArr.index('Starting Points: []')]
print(methods)
#code below is to replace method calls within methods with their text (very annoying)
for line in methods:
    print(line)
    matches ={x.lower() for x in methods if x.split(': ')[0].lower() in line.split(': ')[1].lower()}
    matches = list(matches)
    methodSplit = splitBrack(line.lower().split(': ')[1])
    print(methodSplit)
    print(matches)
    for match in matches:
        for text in methodSplit:
            #if "this.subscribe" in text:
                #break
            print(match.split(': ')[0])
            print(text)
            if match.split(': ')[0] in text:
                print("HELLO")
                #TEST THIS WITH DIFFERENT OUTPUT, DOESN'T WORK WITH c02 MONITOR BECAUSE NO METHODCALLS WITHIN METHODS
                methodSplit[methodSplit.index(text)] = re.sub(re.escape(match.split(': ')[0]) + '\(.*\)', match.split(': ')[1], text, flags=re.IGNORECASE)
    methods[methods.index(line)] = line.split(': ')[0] + ': ' + ''.join(methodSplit)
#replace

#testApp = app(string)
