import sqlite3
import itertools
import fnmatch
from collections import OrderedDict
from itertools import chain
import re




#=============================================================================#
#getRelationalSchema(relation)
#gets the colums of the table specified
#returns 2 lists, LHS, RHS attributes
#parameters: relation, is the number the user enters which specifies which table
#=============================================================================#

def getRelationalSchema(relation):
    table_name = 'Input_R'+relation
    # GET COLUMN NAMES
    sql = "PRAGMA table_info("+table_name+")"
    c.execute(sql)
    col_names = c.fetchall()
    #print col_names
    # This is the list of column names
    col= []
    for i in range (len(col_names)):
        col.append(str(col_names[i][1]))
    #print 'Columns of R'+relation,col

    # GET FUNCTIONAL DEPENDENCIES
    # get LHS
    table_fds = 'Input_FDs_R'+relation
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
    
    return LHS,RHS

#=============================================================================#
#getMinimalCover(left, right)
#finds the minimal coverage, calling on several methods
#parameters: left - lhs attributes
#            right - rhs attributes
#=============================================================================#

def getMinimalCover(left, right):
    #step 1: right hand side singleton
    l, r = getSingleton(left, right)
    #print 'singleton'
    #print l
    #print r
    
    #step 2: left hand side extraneous attributes
    newl,newr=step2(l, r) #manipulates l and r
    #print 'Step 2: Removed LHS extraneous attributes'
    #print 'new l',newl,'\nnew r',newr
    
    #step 3: Remove redundant FD's
    rl,rr = step3(newl,newr)
    left, right = convert_to_list(rl, rr)
    #print 'Step 3: Removed redundant FDs'
    #print left
    #print right
    
    
    # Combine into functional dependancies, and return the minimal cover FD
    minimal_FD = []
    for i in range(len(left)):
        minimal_FD.append(left[i]+'->'+right[i])
    print '==================================================================='
    print 'Minimal Cover', minimal_FD, '\n' 
    print '==================================================================='
    
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
        items = ''.join(sorted(items)) #change to alphabetical order
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
    #print 'singleton LIST',singleton
    
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
            #print '\nl list removed redundancy ',L_list,'\n'
            #print '\nr list removed redundancy', R_list
    return L_list, R_list   

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
    #print 'reduced l list', reduced_l_list
    #print 'reduced r list', reduced_r_list
    #removed redundant FDs
    for i in range(len(l_list)):
    #find closure of current FD (exclude current FD)
        #print 'STEP 3 INDEX ', i
        l_copy = list(l_list)
        r_copy = list(r_list)
        #print 'STEP 3 l copy', l_copy
        #print 'STEP 3 r copy', r_copy        
        l_copy.pop(i)
        r_copy.pop(i)
        #print 'STEP 3 l copy removed 1 fd', l_copy
        #print 'STEP 3 r copy removed 1 fd', r_copy
        closure = getClosure(l_list[i],l_copy, r_copy)
        #print "closure of T-",l_list[i],"->",r_list[i],closure
        #if RHS of FD is not in the closure, then this FD is not redundant, add it to reduced lists
        if not r_list[i].issubset(closure):
            reduced_l_list.append(l_list[i])
            reduced_r_list.append(r_list[i])
            #print "** reduced fd list", reduced_l_list
            #print "** reduced fd list", reduced_r_list
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
        #print attribute,"closure: ", closure
        # save the closures, per attriute
        if RHS.issubset(closure):
            #print "removed", letter
            
            LHS.remove(letter)
            #print "remaining", LHS
            l_list[i] = LHS

        
    #print "from remove_redundancy", closure
    
#gets closure of a set of attributes
#atribute is a set {'A','B','C'}
#l_list is a list of LHS FDs
#r_list is the corresponding list of RHS FDs

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
            #print "index", f
            #print "current closure", closure_set
            #print 'l copy', l_copy
            #print 'r copy', r_copy            
            if r_copy[f] == '':
                continue
            elif l_copy[f].issubset(closure_set):
                #print "issubset"
                #print r_copy[f]
                #print r_copy
                addtoset(r_copy[f],closure_set)
                #print "added", closure_set
                r_copy[f]=''
                #f+=1
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
def third_normal(LH, RH):
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

    LH = third_norm.keys()
    RH = [third_norm[item] for item in LH]
    
    threenf = []
    for i in range(len(LH)):
        threenf.append(LH[i]+'->'+RH[i])
    return  threenf, LH, RH
        
#=============================================================================#
# output_schema
# creates a view of the output of the normalized data
#=============================================================================#
def output_schema(LH, RH, file_num):
    r = LH + RH
    r = ''.join(r)
    r = set(r)
    r_list = list(r)
    r = ''.join(r_list)
  
    inp = 'INPUT_R'+str(file_num)
    name = 'OUTPUT_R'+str(file_num)+'_'+r
    sql = 'create view '+name+' AS '+'SELECT '
    for i in r_list:
        sql+=(i+',')
    sql = sql[:-1]
    sql+=' FROM '+inp+';'
    #print sql
    drop = "DROP VIEW IF EXISTS "+name

    c.execute(drop)
    c.execute(sql)    
#=============================================================================#
# output_FD
# creates a view of the output of the normalized functional dependancies
#=============================================================================#
def output_FD(LH, RH, file_num):
    r = LH + RH
    r = ''.join(r)
    r = set(r)
    r_list = list(r)
    r = ''.join(r_list)    
    name = 'OUTPUT_FDs_R'+str(file_num)+'_'+r
    inp = 'INPUT_FDs_R'+str(file_num)
    sql = 'create view '+name+' AS SELECT LHS, RHS FROM '
    sql+= inp+';'
    #print sql
    drop = "DROP VIEW IF EXISTS "+name
  
    c.execute(drop)
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
    #print table_names                                                                           
    
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

#db = raw_input('HELLO! Please enter the database name: ')
#conn = sqlite3.connet(db)

#for testing only, delete this before we submit
conn = sqlite3.connect('MiniProject2-InputExample.db')

c = conn.cursor()

#ask user to pick relation
#relation = pickRelation()

# spits the fd into 2 lists
#L,R = getRelationalSchema(relation)

#get minimal cover of FDs
#getMinimalCover(L,R)
#TNF, LH, RH = third_normal(L, R)
#output_schema(LH, RH, relation)
#output_FD(LH, RH, relation) 

# prompt user to pick an action:
# 1.3NF
# 2.BCNF
# 3.Get Closure of an attribute. Have user specify an attribute set, tables(union of these tables as F)
# 4.Check equivalency F1 and F2. Get minimal cover of F1 and F2 and see if they are the same??
while True:
    
    print "Available Operations: \n[1] 3NF\n[2] BCNF\n[3] Get Closure\n[4] Check Equivalency of F1 and F2"
    op = raw_input("Please enter an operation or 'quit' to quit: ").lower()
    
    if op == '1':
        #ask user to pick relation
        relation = pickRelation()
        
        # spits the fd into 2 lists
        L,R = getRelationalSchema(relation)     
        
        #get 3NF
        TNF,LH,RH = third_normal(L,R)
        
        #
        output_schema(LH, RH, relation)
        output_FD(LH, RH, relation)         
        
    elif op == '2':
        pass
    elif op == '3':
        #get attribute set and tables
        a=raw_input("Enter attribute set: ").upper()
        print
        a_set = set()
        
        for letter in a:
            a_set.add(letter)
        t=raw_input("Enter table numbers in the format '1,2,4': ")
        tables = t.split(',')
        
        #add all FDs together
        l = []
        r = []        
        for table in tables:
            table_l, table_r = getRelationalSchema(table)
            l+=table_l
            r+=table_r
        #print 'lhs',l
        #print 'rhs',r
        
        #convert lhs and rhs into singleton list of sets
        sl,sr = getSingleton(l,r)
        #print 'singleton l',sl
        #print 'singleton r',sr

        #get closure of F
        closure = getClosure(a_set, sl,sr)
        print '==================================================================='
        print 'Closure of '+a+' with relation(s) '+ t+':' , list(closure)
        print '==================================================================='
        
   
    elif op == '4':
        #prompt user to pick 2 tables
        print 'Pick F1'
        f1 = pickRelation()
        
        print 'Pick F2'
        f2 = pickRelation()
        
        #get min cover of F1, get min cover of F2
        F1L,F1R = getRelationalSchema(f1)
        F2L,F2R = getRelationalSchema(f2)
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
        break
    else:
        print 'Invalid operation.'
        print 'Try again.'
        print
        print
