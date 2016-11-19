import sqlite3
import itertools
from collections import OrderedDict


conn = sqlite3.connect('MiniProject2-InputExample.db')
c = conn.cursor()

def connectDatabase():

    # GET TABLE NAMES
    c.execute("SELECT name FROM sqlite_master;")
    table_names = c.fetchall()
    #print table_names
    # 1 list of the table names
    table = []
    for i in range(len(table_names)):
        for j in range(len(table_names[i])):
            table.append(str(table_names[i][j]))
    #print table 
    
    # GET COLUMN NAMES
    c.execute("PRAGMA table_info(Input_R1)")
    col_names = c.fetchall()
    #print col_names
    # This is the list of column names
    col= []
    for i in range (len(col_names)):
        col.append(str(col_names[i][1]))
    #print col
    
    # GET FUNCTIONAL DEPENDENCIES
    # get LHS
    c.execute("select LHS from Input_FDs_R1;")
    lhs = c.fetchall()
    LHS = []
    for i in range(len(lhs)):
        for j in range(len(lhs[i])):
            LHS.append(''.join(str(lhs[i][j]).split(',')))
    #print 'LHS',LHS
    #get RHS
    c.execute("select RHS from Input_FDs_R1;")
    rhs = c.fetchall()
    RHS = []
    for i in range(len(rhs)):
        for j in range(len(rhs[i])):
            RHS.append(''.join(str(rhs[i][j]).split(',')))
    
    return LHS,RHS

def getMinimalCover(left, right):
    #step 1: right hand side singleton
    l, r = getSingleton(left, right)
    
    #step 2: left hand side extraneous attributes
    step2(l, r)
    

def getSingleton(oldLeft, oldRight):
    singleton = []
    for i in range(len(oldRight)):
        if len(oldRight[i])> 1:    
            for letter in range(len(oldRight[i])):
                singleton.append(oldLeft[i]+'->'+oldRight[i][letter])
        else:
            singleton.append(oldLeft[i]+'->'+oldRight[i])
    print 'singleton LIST',singleton
    
    # turn into list of sets
    newLeft = []
    newRight=[]
    
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
    #print newLeft
    #print newRight
    return newLeft, newRight
       
       
def step2(L_list, R_list):
    for attribute in L_list:
        if len(attribute)>1:
            remove_redundancy(attribute, L_list, R_list)
    
        
def remove_redundancy(attribute, l, r):
    print attribute
    for letter in attribute:
        attri = attribute.difference(letter)
        #print attri
        getClosure(attri, l, r)
        
def getClosure(attri, l, r):
    # adds the clos
    closure_set = set()
    addtoset(attri, closure_set)
    
    #print "close",closure_set

         
    f = 0
    #print len(l)-1
    while f<(1):
        if l[f].issubset(closure_set):
            print "went to if"
            addtoset(r[f],closure_set)
            f = 0
        else :
            f += 1
    print "hello?", closure_set
           
def addtoset(set1,set2):
    for letter in set1:
        set2.add(letter)
           
                   

#def redundancy(attribute, fd):

    ##we call closure in here
    #closure_list = [attribute]
    #closure(left, right, attribute, closure_list)
    #close = eliminate_dupes(closure_list)
    #print attribute+" closure: ", close

def closure(l, r, attribute, closure_list):
    #initialize closure to list with the attribute
    close = [attribute]
    for i in range(len(l)):
        if attribute == l[i]:
            #check if attribute already exists
            for a in close:
                if a== r[i]:
                    continue
                else:
                    close.append(r[i])
    closure_list.append(close)
    print "closure of c", close
    print "all", closure_list
    
    k=1    
    while k < len(close):
        closure(l,r, close[k], closure_list) 
        k+=1
        

#def eliminate_dupes(closure_list):
    #one =  list(itertools.chain.from_iterable(closure_list))
    #one = set(one)
    #one = list(one)
    #one = ''.join(one)
    #return one
    
    
        
        
    
############################
#         MAIN             #
############################  
# spits the fd into 2 lists
L,R = connectDatabase()

getMinimalCover(L,R)







    

