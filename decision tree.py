import pickle
import math
import json


# The top level class, this basically is a holder for an attribute or value
class node:
    # used to easily identify the type of node
    typ = ""
    # The total number of objects this node applies to
    total = 0
    # The entropy of the split between the outcomes of the objects
    entropy = 0

# This is the top level node, not sematically useful
class root(node):
    typ = "root"
    # The split of the outcomes eg. {success: 5, failure: 5}
    outcomes = {}
    entropy = 0
    def __init__(self):
        # initialize the outcomes
        for obj in data:
            self.outcomes[obj[success]] = 0
        # count the outcomes
        for obj in data:
            self.outcomes[obj[success]] += 1
        # get the entropy of the root
        self.entropy = getEntropy(self.outcomes)
    
    # sets the only child to the root
    def setChild(self, child):
        self.child = child
    
# an Attribute node holds an attribute of the dataset
class att(node):
    typ = "att"
    # it has a number of children to further define it. 
    # the object is accessed by self.children[self][value]
    # because for some reason python does not want to create
    # new instances of this one object
    children = {}
    # The name of the attribute this node represents
    attribute = ""
    # The number of outcomes that this node can have
    outcomes = {}
    # come back to here
    parentSet = True
    # requires an attribute, a parent node, and a value 
    # that the node branches from
    def __init__(self, attribute, parent, value):
        self.attribute = attribute
        self.parent = parent
        # initialize the children object for this node
        self.children[self] = {}
        if parent.typ == "root":
            self.parentSet = False
        else:
            self.parentValue = value
        # get the outcomes
        for sOutcome in successOutcomes:
            self.outcomes[sOutcome] = 0
        # get the possible values of this attribute
        values = getValues(attribute)
        # populate the outcomes
        for obj in data:
            for value in values:
                for sOutcome in successOutcomes:
                    if testOutcome(obj, self, value) == True and obj[success] == sOutcome:
                        self.outcomes[sOutcome] += 1
        # get the entropy determined by the outcomes
        self.entropy = getEntropy(self.outcomes)
        
    # add a child node to this node
    def addChild(self, nod, child, value):
        self.children[nod][value] = child
    
    # print the tree starting at this node
    def printt(self, depth):
        depth += 1
        for child in self.children[self].keys():
            for d in range(0, depth):
                    print("\t", end="")
            if self.children[self][child].typ == "att":
                print(self.children[self][child].parentValue+": "+self.children[self][child].attribute)
                self.children[self][child].printt(depth)
            elif self.children[self][child].typ == "val":
                print(self.children[self][child].parentValue+": "+str(self.children[self][child].outcome))
                
# a value node, this much simpler becuse it
# basically just has to hold a value and have a parent
class val(node):
    typ = "val"
    value = ""
    outcomes = {}
    def __init__(self, outcome, parent, value):
        self.outcome = outcome
        self.parent = parent
        self.parentValue = value

# outcomes is a dictionary that holds the number of times each outcome happens
# gets the entropy of a set of outcomes
# The entropy determines the unlikelyness of a set of outcomes to happen
def getEntropy(outcomes):
    # the total number of outcomes
    total = 0
    for outcome in outcomes.keys():
        total += outcomes[outcome]
    ent = 0
    for outcome in outcomes.keys():
        # if there are no outcomes
        # it is 100% unpredictable
        # and therefore entropy is 1
        if total == 0:
            ent += 1
            break
        # as long as there outcome is at least one of these outcomes
        # log cannot be taken of zero, but the limit is 0
        if (outcomes[outcome]/total) != 0:
            ent -= (outcomes[outcome]/total)*math.log((outcomes[outcome]/total), 2)
    return ent

# get all the possible values of a specific attribute
def getValues(attribute):
    values = []
    for obj in data:
        values.append(obj[attribute])
    # make sure there are no duplicates
    return set(values)

# The information gain represents how
# much information is gained if a branch is placed
# from this node to the next attribute
def getInformationGain(nod, attribute):
    # get the entropy of the parent node
    eBefore = getEntropy(nod.outcomes)
    # the set of entropy values for each possible value of that attribute
    eValues = {}
    values = getValues(attribute)
    outcomes = {}
    for value in values:
        eValues[value] = {}
        outcomes[value] = {}
        for sOutcome in successOutcomes:
            outcomes[value][sOutcome] = 0
    # get the values for entropy on each value
    for value in values:
        for obj in data:
            for sOutcome in successOutcomes:
                if nod.typ == "root":
                    if obj[attribute] == value and obj[success] == sOutcome:
                        outcomes[value][sOutcome] += 1
                else:
                    if testOutcome(obj, nod, value) and obj[success] == sOutcome:
                        outcomes[value][sOutcome] += 1
        eValues[value]['e'] = getEntropy(outcomes[value])
    # for the average each entropy must have a weight
    # depending upon the amount of times that outcome
    # occurs compared to the total, this is given by the 'top'
    # part of the eValues
    total = 0
    for value in values:
        eValues[value]['top'] = 0
        for sOutcome in successOutcomes:
            eValues[value]['top'] += outcomes[value][sOutcome]
        total += eValues[value]['top']
    # The entropy after this transformation takes place is
    # is the weighted average of all the outcome entropies
    eAfter = 0
    for value in values:
        eAfter += (eValues[value]['top']/total)*eValues[value]['e']
    # subtract one from the other to get the information gain
    return eBefore - eAfter

# A recursive method that determines if an outcome takes place
# with context of its parent nodes. 
def testOutcome(obj, nod, outcome):
    # start from the bottom and work upwards
    # test if the object has that outcome for the attribute
    if obj[nod.attribute] == outcome:
        # if the node has a parent
        if nod.parentSet == True:
            # test if the object also has it's parent value true
            return testOutcome(obj, nod.parent, nod.parentValue)
        else:
            return True
    else:
        return False

# Fill a set of values with nodes, whether they are
# attributes or values
def fillRow(nod, ignore):
    # get all the values for this attribute
    values = getValues(nod.attribute)
    # the gains show a detailed list of all the gains
    # of each attribute
    gains = {}
    # The attributes that are tested
    attributes = []
    skip = False
    # put all the attributes of data into a list, making sure the ones to ignore are not on that list
    for key in data[0].keys():
        for ig in ignore:
            if ig == key:
                skip = True
        if skip == False:
            attributes.append(key)
        skip = False
    # Go through each value to determine if all
    # of the objects for this value result in one outcome
    for value in values:
        valOutcomes = {}
        total = 0
        out = ""
        for sOutcome in successOutcomes:
            valOutcomes[sOutcome] = 0
        for obj in data:
            for sOutcome in successOutcomes:
                if testOutcome(obj, nod, value) and obj[success] == sOutcome:
                    valOutcomes[sOutcome] += 1
        for outcome in valOutcomes.keys():
            total += valOutcomes[outcome]
        for outcome in valOutcomes.keys():
            if valOutcomes[outcome] == total:
                out = outcome
                break
        # if it is all one outcome, create a value node at that value
        # saying the outcome that it is guarenteed to happen
        if out != "":
            nod.addChild(nod, val(out, nod, value), value)
        else:
            # for all the remaining values, get the infomation gain of
            # each to determine which one is best suited to go where
            gains[value] = {}
            for attribute in attributes:
                i = getInformationGain(att(attribute, nod, value), attribute)
                gains[value][attribute] = i
    # This is to make sure that two values do not get the same attribute split on
    while True:
        pas = True
        # seperates the gains into an easily sortable list
        infos = []
        # This holds the highest gain for each value of the node's attribute
        highest = {}
        for value in gains.keys():
            # initialize the value with -2 gain (Nothing can have this low of a gain)
            highest[value] = {'gain': -2}
            # determine which attribute is the highest
            for attribute in gains[value].keys():
                obj = {
                    'value': value,
                    'attribute': attribute,
                    'gain': gains[value][attribute]
                }
                infos.append(obj)
                for info in infos:
                    if info['gain'] > highest[info['value']]['gain']:
                        highest[info['value']] = info
        # turn the dictionary into a list for easier access
        arr = []
        for value in highest.keys():
            arr.append(highest[value])
        # determine if the attribute is suited best for two different values
        for a in range(1, len(arr)):
            if arr[a]['attribute'] == arr[a-1]['attribute']:
                pas = False
                # if a duplicate is found, add it to the ignore list
                ignore.append(arr[a]['attribute'])
                # check which one of the gains is higher and create a node on that one
                if arr[a]['gain'] > arr[a-1]['gain']:
                    nod.addChild(nod, att(arr[a]['attribute'], nod, arr[a]['value']), arr[a]['value'])
                    fillRow(nod.children[arr[a]['value']], ignore[:])
                elif arr[a-1]['gain'] > arr[a]['gain']:
                    nod.addChild(nod, att(arr[a-1]['attribute'], nod, arr[a-1]['value']), arr[a-1]['value'])
                    fillRow(nod.children[arr[a-1]['value']], ignore[:])
                # destroy all of the gains of that attribute
                for value in gains.keys():
                    gains[value].pop(attribute)
                gains.pop(value)
        if pas == True:
            break
    # in every part of the array, create a new attribute node for that value
    # and fill in the row
    for a in arr:
        if a['gain'] != -2:
            ignore.append(a['attribute'])
            nod.addChild(nod, att(a['attribute'], nod, a['value']), a['value'])
            fillRow(nod.children[nod][a['value']], ignore[:])
        
def level(obj, nod):
        if nod.typ == "val":
            return nod.outcome
        elif nod.typ == "att":
            for value in getValues(nod.attribute):
                if obj[nod.attribute] == value:
                    return level(obj, nod.children[nod][value])
    
def testData():
        for obj in test:
            print(obj[index]+": "+level(obj, n))
            


print("Decision Tree Interface")
while True:
    print("1. Create Tree")
    print("2. Load Tree")
    print("3. Save Tree")
    print("4. Test Data")
    cmd = input("Cmd: ")
    if cmd == '1':
        ign = []
        data = json.loads(open(input("\nSpecify file: ")).read())
        # The success attribute
        success = input("success attribute: ")
        # the index attribute (unique ID)
        index = input("index attribute: ")
        while cmd != "quit":
            cmd = input("tag to ignore(type quit to skip): ")
            if cmd != "quit":
                ign.append(cmd)
        # get all the possible outcomes of the success attribute
        successOutcomes = []
        for obj in data:
            successOutcomes.append(obj[success])
        successOutcomes = set(successOutcomes)
        # create a dummy root node
        r = root()
        gain = 0
        highestGain = ["", 0]
        skip = False
        # put all the attributes of data into a list, making sure the ones to ignore are not on that list
        ign = [index, success]
        attributes = []
        for key in data[0].keys():
            for ig in ign:
                if ig == key:
                    skip = True
            if skip == False:
                attributes.append(key)
            skip = False
        # get the initital highest gain
        for attribute in attributes:
            gain = getInformationGain(root, attribute)
            if gain > highestGain[1]:
                highestGain[0] = attribute
                highestGain[1] = gain
        # create a new node that splits with the attribute with the highest gain
        n = att(highestGain[0], r, "")
        # fill the row if that node
        fillRow(n, [success, n.attribute, 'Film'])
        # Print the resulting tree
        print("\n\n")
        print(n.attribute)
        n.printt(0)
        print("\n\n")
    elif cmd == '2':
        try:
            n
        except NameError:
            print("Tree is not loaded")
        else:
            print (n)
            n = pickle.load(open(input("file: "), "rb"))
    elif cmd =='3':
        pickle.dump(n, open(input("file: "), "wb"))
        print("tree: ")
        n.printt(0)




