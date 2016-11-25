import sqlite3
import itertools
import fnmatch
from collections import OrderedDict
from itertools import chain, combinations
import re
import sys

#==============================================================================#
# A class to hold the relations.
# Used to store decomposed relations (or any relation).
#==============================================================================#
class relations:
    def __init__(self):
        self.keys = set() # keys of the relation
        self.attributes = set() # all attributes
        self.FDs = [] # functional dependancies in tuples (LH, RH)

    def print_rel(self): # for debugging
        print "attributes:", self.attributes
        print "keys:", self.keys
        print "Functional Dependancies:"
        self.printFDs()
        print '-'*80

    def add_FDs(self, LH, RH): # makes things easier in BCNF
        for i in range(len(LH)):
            self.FDs.append((LH[i], RH[i]))

    def printFDs(self): # to only print FDs
        for fd in self.FDs:
            print fd[0], '->', fd[1]

#=============================================================================#
#getRelationalSchema(relation)
#gets the colums of the table specified
#returns:
# LHS of FDs of the relation (list of strings )
# RHS of FDs of the relation (list of strings)
# All column names of relation (list of strings)
# Corresponding column types of the relation (list of strings)
#parameters: relation, is the number the user enters which specifies which table
#=============================================================================#

def getRelationalSchema(relation):
    table_name = 'Input_R'+str(relation)

    # GET COLUMN NAMES
    sql = "PRAGMA table_info("+table_name+");"
    c.execute(sql)
    cols = c.fetchall()

    # This is the list of column names
    col_names = []
    col_types = []
    for i in range (len(cols)):
        col_names.append(str(cols[i][1]))
        col_types.append(str(cols[i][2]))

    # GET FUNCTIONAL DEPENDENCIES
    # get LHS
    table_fds = 'Input_FDs_R'+str(relation)
    sql = "select LHS from "+table_fds+";"
    c.execute(sql)
    lhs = c.fetchall()
    LHS = []
    for i in range(len(lhs)):
        for j in range(len(lhs[i])):
            LHS.append(''.join(str(lhs[i][j]).split(',')))
    #get RHS
    sql = "select RHS from "+table_fds+";"
    c.execute(sql)
    rhs = c.fetchall()
    RHS = []
    for i in range(len(rhs)):
        for j in range(len(rhs[i])):
            RHS.append(''.join(str(rhs[i][j]).split(',')))

    return LHS,RHS, col_names, col_types

#=============================================================================#
#getMinimalCover(left, right)
#finds the minimal coverage, calling on several methods
#parameters: left - lhs attributes
#            right - rhs attributes
#=============================================================================#

def getMinimalCover(left, right):
    #step 1: right hand side singleton
    l, r = getSingleton(left, right)

    #step 2: left hand side extraneous attributes
    newl,newr=step2(l, r) #manipulates l and r

    #step 3: Remove redundant FD's
    rl,rr = step3(newl,newr)
    left, right = convert_to_list(rl, rr)

    # Combine into functional dependancies, and return the minimal cover FD
    minimal_FD = []
    for i in range(len(left)):
        minimal_FD.append(left[i]+'->'+right[i])
    #print '==================================================================='
    #print 'Minimal Cover', minimal_FD, '\n'
    #print '==================================================================='

    return minimal_FD

#=============================================================================#
#convert_to_list(rl, rr)
#coverting the sets to lists from the third step of minimal cover
#paramters: rr, reduced right list
#           rl, reduced left list
#=============================================================================#
# converts the reduced list of sets into list of lists
def convert_to_list(rl, rr):
    left = []
    right = []
    for items in rl:
        items = ''.join(sorted(items)) #change string to alphabetical order
        #change type
        l = list(items)
        left.append(l)
    for i in rr:
        i = ''.join(sorted(i))
        r = list(i)
        right.append(r)
    l = []
    for item in left:
        x=''.join(item)
        l.append(x)
    right =list(chain.from_iterable(right))
    return l, right

#=============================================================================#
# getSingleton(oldLeft, oldRight)
# step one of min cover, seperate all attributes on RHS to single attribute
#
# input oldLeft: list of attribute strings e.g.['ABH','EF','S']
# input oldRight: list of attribute strings
#=============================================================================#

def getSingleton(oldLeft, oldRight):
    singleton = []
    for i in range(len(oldRight)):
        if len(oldRight[i])> 1:
            for letter in range(len(oldRight[i])):
                singleton.append(oldLeft[i]+'->'+oldRight[i][letter])
        else:
            singleton.append(oldLeft[i]+'->'+oldRight[i])

    # turn into list of sets
    newLeft = []
    #this is still a list
    newRight = []

    for i in range(len(singleton)):
        splitFD = singleton[i].split('->')
        #we get new lists
        newLeft.append(splitFD[0])
        newRight.append(splitFD[1])

    for j in range(len(newLeft)):
        s = set()
        for letter in newLeft[j]:
            s.add(letter)
        newLeft[j] = s
        sr = set()
        for l in newRight[j]:
            sr.add(l)
        newRight[j]= sr
    return newLeft, newRight

#=============================================================================#
# step2
# removes the redundancy in the LHS, by callin on remove_redudancy method
#
# input L_list: singleton list of sets of lhs attributes
# input R_list: singleton list of sets of rhs attributes
# output L_list: input L_list with redundant lhs attributes removed
# output R_list: unchanged from input R_list
#=============================================================================#
def step2(L_list, R_list):
    for j in range(len(L_list)):
        if len(L_list[j])>1:
            remove_redundancy(L_list[j], R_list[j], L_list, R_list)

            
    l, r = convert_to_list(L_list, R_list)
    test = []
    for i in range(len(l)):
        test.append(l[i]+'->'+r[i])
   
    # to remove duplicate FD's, incase there are only 2 and they are the same  
    test = set(test)
  
    # turn in back into sets, for the parameters of rest of min cover
    test = list(test)
    
    l_list = []
    r_list = []    
    #list = []
    for i in range(len(test)):
        split = test[i].split('->')
        l_list.append(split[0])
        r_list.append(split[1])
        
    for j in range(len(l_list)):
            s = set()
            for letter in l_list[j]:
                s.add(letter)
            l_list[j] = s
            sr = set()
            for l in r_list[j]:
                sr.add(l)
            r_list[j]= sr
        
       
    #print l_list 
    #print r_list
    return l_list, r_list
    

#=============================================================================#
# step3
# removes redundant dependancies by comparing the attribute with the closure
#
# input l_list: output of step2()
# input r_list: output of step2()
#=============================================================================#
def step3(l_list, r_list):
    reduced_l_list = []
    reduced_r_list = []
    #removed redundant FDs
    for i in range(len(l_list)):
    #find closure of current FD (exclude current FD)
        l_copy = list(l_list)
        r_copy = list(r_list)
        l_copy.pop(i)
        r_copy.pop(i)
        closure = getClosure(l_list[i],l_copy, r_copy)
        #if RHS of FD is not in the closure, then this FD is not redundant, add it to reduced lists
        if not r_list[i].issubset(closure):
            reduced_l_list.append(l_list[i])
            reduced_r_list.append(r_list[i])
    return reduced_l_list, reduced_r_list


#=============================================================================#
# remove_redundancy(LHS, RHS, l_list, r_list)
# removes any redundant letters on the lhs of an FD
# e.g. ABH->C becomes BH->C
# changes l_list and r_list
#
# input LHS: set of lhs attributes
# input RHS: set of rhs attributes
# input l_list: same input as step2()
# input r_list: same input as step2()
#=============================================================================#
def remove_redundancy(LHS, RHS, l_list, r_list):
    LHS_copy = set(LHS)
    i = l_list.index(LHS)

    for letter in LHS_copy:
        attribute = LHS_copy.difference(letter)
        closure = getClosure(attribute, l_list, r_list)
        # save the closures, per attriute
        if RHS.issubset(closure):
            LHS.remove(letter)
            l_list[i] = LHS


#=============================================================================#
# getClosure(attribute, l_list, r_list)
# finds the closure of attribute
#=============================================================================#
def getClosure(attribute, l_list, r_list):
    #get copies of l and r
    l_copy = list(l_list)
    r_copy = list(r_list)

    # adds the closure
    closure_set = set()
    addtoset(attribute, closure_set)

    added=True
    while added == True:
        added = False
        for f in range(len(l_copy)):
            if r_copy[f] == '':
                continue
            elif set(l_copy[f]).issubset(closure_set):
                addtoset(r_copy[f],closure_set)
                r_copy[f]=''
                added = True
            else :
                continue
    return closure_set

#=============================================================================#
# add to set(set1, set2)
# method to add a number to the set, because in other methods, the sets are
# stored as a list of sets
#=============================================================================#
def addtoset(set1,set2):
    for letter in set1:
        set2.add(letter)



#==============================================================================#
# findPrime(LH, RH, f)
# Finds the prime attributes of the relation.
# Returns: a set of prime attributes.
# parameters: LH - left hand side of FDs
#             RH - right hands side of FDs
#==============================================================================#
def findPrime(LH, RH, f):
    keys = find_key(LH,RH,f)
    prime_attributes = set(''.join(keys))
    return prime_attributes

#==============================================================================#
# findKeys(LH, RH, F)
# Finds all the keys of the relation. All keys are minimal
# returns: keys -  a list of keys of the realtion.
# parameters: LH, RH, F. left hand, right hand of FDs and all attributes.
#==============================================================================#
def find_key(LH, RH, F):
    keys = []

    LHS = set(''.join(LH))
    RHS = set(''.join(RH))


    left = LHS - RHS
    middle = LHS & RHS

    left = ''.join(left)

    # attributes not in any FDs must be in the key.

    otherA = set(F) - (LHS | RHS)
    left = left + ''.join(otherA)

    # attributes only on the left must be in the key.
    if left:
        if getClosure(left, LH, RH) == set(F):
            keys.append(left)
            return keys

    middle.add(left)

    for item in powerset(middle):
        if not item or left not in item:
            continue

        closureX = getClosure(''.join(item), LH, RH)
        if closureX == F:
            keys.append(''.join(i))

    minimal = len(keys[0])

    for i in range(1,len(keys)):
        if len(keys[i]) > minimal:
            return keys[:i]

    return keys

# function from https://docs.python.org/2/library/itertools.html
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

#==============================================================================#
# check_bcnf(LH, RH, F)
# checks if F is in bcnf.
# parameters: LH - left hand side of FDs
#             RH - right hands side of FDs
#             F - all attributes
# Returns: violating: a list of violating FDs referenced by index.
#==============================================================================#
def check_bcnf(LH,RH,F):
    violating =[]
    for i in range(len(LH)):
        closureX = getClosure(LH[i], LH, RH)

        if len(closureX) == len(F): # if LH is a key
            continue

        LRintersection = [x for x in RH if x in LH] # if RH is a subest of LH
        if len(LRintersection) != len(RH):
            violating.append(i)

    return violating

#==============================================================================#
# check_3nf(LH, RH, F)
# checks if F is already in 3nf. First checks if F is in BCNF. If yes, the function will
# return True, else, it will check if RH of violating FDs are prime attributes
# by calling the function find_prime.
# parameters: LH - left hand side of FDs
#             RH - right hands side of FDs
#             F - all attributes
# Returns: True if not violating, False if violating
#==============================================================================#
def check_3nf(LH,RH,F):
    violating, prime = check_bcnf(LH, RH, F)
    if not violating: # checks if there are any FDs that violate BCNF
        return True

    for fd in violating:
        if len(set(RH[fd]).intersection(prime)) == len(RH[i]):
            continue
        else:
            return False
    return True

#==============================================================================#
# third_normal(minimal_cover)
# Finds 3NF given the minimal cover.
# paramters: minimal_cover : minimal cover of F
# returns: LH - left hand side of FDs after decomposition
#          RH - right hand side  of FDs after decomposition
#==============================================================================#
def third_normal(LH, RH, f):
    #if check_3nf(LH, RH, f):
        #return LH, RH # it's already in 3NF
    minimal_cover = getMinimalCover(LH, RH)

    min_cover = [fd.split("->") for fd in minimal_cover] # split the left and right hand sides
    third_norm = dict()
    # combine fds with the same RHS
    for item in min_cover:
        # if RHS is already exists, then combine LHS.
        if item[0] in third_norm:
            third_norm[item[0]] = third_norm[item[0]] + item[1]
        # if not, add both RHS and LHS to dictionary.
        else:
            third_norm[item[0]] = item[1]

    LHCopy = third_norm.keys()
    RHCopy = [third_norm[item] for item in LHCopy]


    decomp = [] # fill decomp
    for item in third_norm:
        decomp.append(relations())
        decomp[-1].attributes = set(item).union(set(third_norm[item]))
        decomp[-1].keys = set(item)
        decomp[-1].FDs.append((item, third_norm[item]))

    # ensure losslessness:
    if not checkDependency(decomp, LH,  RH, f):
        key = find_key(LH,RH, f) # will add the first key it finds into the relation
        decomp.append(relations())
        decomp[-1].attributes = set(key)
        decomp[-1].keys = set(key)

    return decomp

#==============================================================================#
# bcnf(LH, RH, f)
# bcnf decomposition.
# arguments: LH: left hand side of FD, RH: Right hand side of FD, F: original schema
# returns: -decomp -  a list of decomposed relations.
#          - whether decomposition is dependency preserving (True or False).
#==============================================================================#
def bcnf(LH, RH, f):
    v = check_bcnf(LH,RH,f) #check if any FDs violate BCNF

    current = relations()
    current.add_FDs(LH,RH)
    current.attributes = set(f)

    decomp = []
    while v:

        decomp.append(relations())

        # always chooses the first violating fd found.
        decomp[-1].keys = set(current.FDs[v[0]][0]) # LHS of violating FD
        decomp[-1].attributes = set(''.join(current.FDs[v[0]]))
        decomp[-1].FDs.append(current.FDs.pop(v[0]))

        fRemove = []

        updatedList = list(current.FDs)#removing items while using as loop control causes errors

        for fd in decomp[-1].FDs:
            x = fd[1]
            # remove attributes
            for i in x:
                current.attributes.discard(i)

        # remove FDs where parts of the left are missing
        for fd in current.FDs:
            for attri in fd[0]:
                if attri not in current.attributes:
                    updatedList.remove(fd)

        # remove attributes not in F2 from right side current.attributes
            for attri in fd[1]:
                if attri not in current.attributes:
                    temp = list(fd)
                    temp[1] = temp[1].replace(attri, '')
                    updatedList.insert(current.FDs.index(fd), tuple(temp))
                    updatedList.remove(fd)

        current.FDs = updatedList
        updatedList = list()

        cLH = [fd[0] for fd in current.FDs]
        cRH = [fd[1] for fd in current.FDs]

        v = check_bcnf(cLH, cRH, current.attributes)

    if not current.keys: # if there are no keys added (already in bcnf to begin with)
        if not current.FDs:
            current.keys = current.attributes # all attributes are keys if there are no FDs
        else:
            current.keys = set(find_key(cLH, cRH, current.attributes))

    decomp.append(current)

    DependPres = checkDependency(decomp, LH, RH, f)

    return decomp, DependPres

#==============================================================================#
# checkDependency(decomp, LH, RH)
# checks if decomposition is dependency preserving.
# arguments: Decomp - a list of decomposed relalations. LH, RH: FDs of original schema
# returns: True or False
#==============================================================================#
def checkDependency(decomp, LH, RH, R):
    decompLH = []
    decompRH = []


    # convert form.
    for r in decomp:
        for fd in r.FDs:
            decompLH.append(fd[0])
            decompRH.append(fd[1])

    #check if all FDs of R are in decomp
    if decompLH == LH and decompRH == RH:
        return True

    # if not, check decomp+
    closureDecomp = set()
    for i in range(len(decompLH)):
        closureDecomp = closureDecomp | getClosure(decompLH[i], decompRH[i], R)

    for i in range(len(LH)):
        setFD = set(LH[i]+RH[i])
        if setFD & closureDecomp != setFD:
            return False

    return True
#=============================================================================#
# output_schema
# creates a view of the output of the normalized data
# relation is a set of attributes that is returned, from that we can get the fds
# and keys
#=============================================================================#
def output_schema(relation, table_num, col_names, col_types):
    for r in relation:
        attributes = r.attributes
        attri_string = ''
        for a in attributes:
            attri_string+=a

        #create output relation tables
        inp = 'INPUT_R'+str(table_num) #input_R1_AD
        outp = 'OUTPUT_R'+str(table_num)+'_'+attri_string #output_R1_AD
        sql = 'CREATE TABLE '+outp+'('
        #create empty table input_R1_AD
        r_cols=[]
        for attri in attri_string:
            l = attri.split()
            r_cols += l
        for letter in r_cols:
            l_type = col_types[col_names.index(letter)]
            sql += letter+' '
            sql += l_type
            sql += ','
        sql = sql[:-1]
        sql += ');'
        drop = 'DROP TABLE IF EXISTS '+outp+';'

        c.execute(drop)
        c.execute(sql)

        #populate output table with data from inp

        #insert into output_R1_ABC (A,B,C) select A,B,C from Input_R1;
        ins = 'INSERT INTO '+outp+' ('
        r_col_str = ''
        for letter in r_cols:
            r_col_str += letter+','
        r_col_str = r_col_str[:-1]
        ins += r_col_str+') SELECT '+r_col_str+' from '+inp+';'

        c.execute(ins)

#=============================================================================#
# output_FD
# creates a view of the output of the normalized functional dependancies
#=============================================================================#

def output_FD(relation, file_num):
    # r is the attributes of a relation
    for r in relation:
        attributes = r.attributes
        attributes = ''.join(attributes)

        name = 'OUTPUT_FDs_R'+str(file_num)+'_'+str(attributes)

        #drops the table if it already exists
        drop = 'DROP TABLE IF EXISTS '+name+';'
        c.execute(drop)

        # createst the tables
        sql = 'CREATE TABLE '+name+' ( LHS TEXT, RHS TEXT);'
        c.execute(sql)

        fds = r.FDs  # this is a list of tuples
        for fd in fds:
            #if fd is empty, skip
            if len(fd)<1:
                continue
            l=fd[0]
            r=fd[1]

            sql = 'INSERT INTO '+name+' VALUES ('+'"'+str(l)+'"'+','+'"'+str(r)+'"'+');'
            c.execute(sql)

#=============================================================================#
# pickRelation
# lists all the relation in the database
# asks user to pick a relation
#=============================================================================#
def pickRelation():
    #ask user to choose a relation R
    # GET TABLE NAMES
    c.execute("SELECT name FROM sqlite_master;")
    table_names = c.fetchall()

    # 1 list the table names
    table = []
    for i in range(len(table_names)):
        for j in range(len(table_names[i])):
            if fnmatch.fnmatch(str(table_names[i][j]),'Input_R*'):
                name = str(table_names[i][j])
                splitname = name.split('_')
                table.append(splitname[1])
    print 'All relations: ', table

    while True:
        # prompt user to pick a relation
        relation_num = raw_input('Pick a table by entering its number: ')

        #check if they picked a valid number
        s = 'R'+relation_num
        exist = False
        for item in table:
            if s == item:
                exist = True
        if exist:
            return relation_num
        else:
            print 'Relation does not exist! Pick again'


############################
#         MAIN             #
############################

#open db. If db doesn't exist, exit program.
db = raw_input('HELLO! Please enter the database name: ')

try:
    open(db,'r')
except IOError:
    sys.exit('Database not found!')
    
conn = sqlite3.connect(db)

c = conn.cursor()

# prompt user to pick an action:
# 1.3NF
# 2.BCNF
# 3.Get Closure of an attribute. Have user specify an attribute set, tables(union of these tables as F)
# 4.Check equivalency F1 and F2. Get minimal cover of F1 and F2 and see if they are the same
while True:

    print "Available Operations: \n[1] 3NF\n[2] BCNF\n[3] Get Closure\n[4] Check Equivalency of F1 and F2"
    op = raw_input("Please enter an operation or 'quit' to quit: ").lower()

    if op == '1': #3NF
        #ask user to pick table number
        table_num = pickRelation()

        # spits the fd into 2 lists
        L,R, col_names, col_types = getRelationalSchema(table_num)

        #get 3NF
        all_relations = third_normal(L,R, col_names)
        print '==================================================================='
        for r in all_relations:
            r.print_rel()
        
        # The output data in its proper format
        change = ''
        while (change != 'y' and change != 'n'): 
            change = raw_input("Do you want to add output to the database? (y/n): ")
        if change == 'y':
            print 'Adding tables ...'
            output_schema(all_relations, table_num, col_names, col_types)
            output_FD(all_relations, table_num)
            conn.commit()
            print 'Done.'
        else:
            print "You database was not changed."
        print '==================================================================='

            
    elif op == '2': #BCNF
        #ask user to pick relation ***relation here means: table number***
        table_num = pickRelation()
    
        # spits the fd into 2 lists
        L,R, col_names, col_types = getRelationalSchema(table_num)
    
        #get BCNF
        all_relations, depen_pres = bcnf(L,R, col_names)
        print '==================================================================='
        for r in all_relations:
                    r.print_rel()   
                    
        if depen_pres:
            print 'Decomposition of R'+table_num+' is dependency preserving.'
        else:
            print 'Decomposition of R'+table_num+' is NOT dependency preserving.'
        # The output data in its proper format
        print
        change = ''
        while (change != 'y' and change != 'n'): 
            change = raw_input("Do you want to add output to the database? (y/n): ")
        if change == 'y':
            print 'Adding tables ...'
            output_schema(all_relations, table_num, col_names, col_types)
            output_FD(all_relations, table_num)
            conn.commit()
            print 'Done.'
        else:
            print "You database was not changed."
        print '==================================================================='

        
    elif op == '3':
        #get attribute set and tables
        a=raw_input("Enter attribute set: ").upper()
        print
        a_set = set()

        for letter in a:
            a_set.add(letter)
        #print table numbers
        # GET TABLE NAMES
        c.execute("SELECT name FROM sqlite_master;")
        table_names = c.fetchall()
    
        # 1 list the table names
        table = []
        for i in range(len(table_names)):
            for j in range(len(table_names[i])):
                if fnmatch.fnmatch(str(table_names[i][j]),'Input_R*'):
                    name = str(table_names[i][j])
                    splitname = name.split('_')
                    table.append(splitname[1])
        print 'All relations: ', table      
            
        t=raw_input("Enter table numbers in the format '1,2,4': ")
        tables = t.split(',')

        #add all FDs together
        l = []
        r = []
        for table in tables:
            table_l, table_r, _,_ = getRelationalSchema(table)
            l+=table_l
            r+=table_r

        #convert lhs and rhs into singleton list of sets
        sl,sr = getSingleton(l,r)

        #get closure of F
        closure = getClosure(a_set, sl,sr)
        
        print '==================================================================='
        print 'Closure of '+a+' using FDs of relation(s) '+ t+':' , list(closure)
        print '==================================================================='


    elif op == '4':
        #prompt user to pick 2 tables
        print 'Pick F1'
        f1 = pickRelation()

        print 'Pick F2'
        f2 = pickRelation()

        #get min cover of F1, get min cover of F2
        F1L,F1R,_,_ = getRelationalSchema(f1)
        F2L,F2R,_,_ = getRelationalSchema(f2)
        F1 = getMinimalCover(F1L,F1R)
        F2 = getMinimalCover(F2L,F2R)

        #compare the 2 min covers and see if they are the same!
        equivalent = True
        for item in F1:
            if item not in F2:
                equivalent = False
                
        print '==================================================================='
        if equivalent:
            print 'Equivalent!'
        else:
            print 'Not equivalent!'
        print '==================================================================='

    elif op == 'quit':
        print 'GOOD BYE!'
        break
    else:
        print 'Invalid operation.'
        print 'Try again.'
        print
        print
        

conn.close()
