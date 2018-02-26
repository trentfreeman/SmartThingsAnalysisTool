import re

#TODO: DONT FORGET REPR METHODS
class app:
    def __init__(self,string):
        self.StateVar = []
        self.startNodes = []
        self.findStarts(string)

    def findStarts(self, string):
        arr = []
        for line in string:
            if 'this.subscribe' in  line:
                arr = re.findall(r'this.subscribe\(.*\)', line)
                for item in arr:
                    x= start(item[item.index('(')+1:-1].split(','), string, self)
                    self.startNodes += [x]
        
    def __repr__(self):
        return 'Application ' +self.name + '; Starts: [' + ', '.join(map(repr,self.startNodes)) + ']' 

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


class method:
    def __init__(self, name, text, app):
        self.name = name
        self.app = app
        self.variables = []
        self.tree = createTree(text.split(': ')[1], self, app)


class expresNode():
    def __init__(self, arr, method, app,text):
        self.right = arr[0].strip()
        if len(arr)>1:
            self.left = arr[1].strip()
        self.app = app
        self.method = method
        self.nextNode = parse(text, method, app) 

    def __repr__(self):
        return self.right + ' = ' + self.left 


class ifNode():
    def __init__(self, ifArray, method, app, text):
        self.app = app
        self.method = method
        #TODO: ADD || to if state
        print('ifARRAY')
        print(ifArray)
        self.ifState = ifArray[0].strip().split('&&')
        trueArr = splitBrack(ifArray[1].strip())
        self.trueBranch = parse(trueArr, self.method, self.app)
        if len(ifArray) >2:
            falseArr = splitBrack(ifArray[2].strip())
            self.falseBranch = parse(falseArr, self.method, self.app)
        if len(text)>0:
            self.nextNode = parse(text, self.method, self.app)

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

def createTree(text,method,app):
    textArr = splitBrack(text)
    return parse(textArr, method, app)

def parse(textArr, method, app):
    #TODO: WORK ON PARSING THE IF STATEMENTS/ MAKING GENERAL PARSER (FOR LOOPS, WHILE LOOPS, etc.)
    #for textArr[0] in textArr:
    print(textArr)
    if re.findall(r'\[if|^(,\[if)', textArr[0], flags = re.IGNORECASE): 
        arr = splitCommas(textArr[0])
        print("splitting commas")
        print(arr)
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
    else:
        print("I don't know how to categorize: " + textArr[0])
        return

#TODO: ADD PREPROCESSING TO REPLACE METHOD CALLS WITH METHOD TEXT
#STARTING HERE
#TODO: MAKE THIS READ FROM overprivout.txt (THIS IS A FINAL THING)
f= open('testing.txt','r')
string = f.read()
f.close()
#fix for multiple apps
stringArr = string.split('\n')
methods = stringArr[stringArr.index('DECLARED METHODS') +1:stringArr.index('Starting Points: []')]
#code below is to replace method calls within methods with their text (very annoying)
for line in methods:
    matches ={x.lower() for x in methods if x.split(': ')[0].lower() in line.split(': ')[1].lower()}
    matches = list(matches)
    methodSplit = splitBrack(line.lower().split(': ')[1])
    for match in matches:
        for text in methodSplit:
            #if "this.subscribe" in text:
                #break
            if match.split(': ')[0] in text:
                #TEST THIS WITH DIFFERENT OUTPUT, DOESN'T WORK WITH c02 MONITOR BECAUSE NO METHODCALLS WITHIN METHODS
                methodSplit[methodSplit.index(text)] = re.sub(re.escape(match.split(': ')[0]) + '\(.*\)', match.split(': ')[1], text, flags=re.IGNORECASE)
    methods[methods.index(line)] = line.split(': ')[0] + ': ' + ''.join(methodSplit)
#replace
stringArr[stringArr.index('DECLARED METHODS') +1:stringArr.index('Starting Points: []')] = methods
testApp = app(stringArr)