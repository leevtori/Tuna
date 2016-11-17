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
    #print 'RHS',RHS  
    
    return LHS,RHS

def getMinimalCover(left, right):
    oldFD = []#list of FD strings
    singleton= []
    for i in range(len(left)):
        oldFD.append(left[i]+'->'+right[i])
    print oldFD
    
    #step 1: right hand side singleton
    for j in range(len(right)):
        if len(right[j])> 1:
            for letter in range(len(right[j])):
                singleton.append(left[j]+'->'+right[j][letter])
        else:
            singleton.append(left[j]+'->'+right[j])
    print 'singleton',singleton
    
    #step 2: left hand side extraneous attributes
    redundancy('C', singleton)
    return


def redundancy(attribute, fd):
    #split into left and right
    left=[]
    right=[]
    for i in range(len(fd)):
        splitFD = fd[i].split('->')
        left.append(splitFD[0])
        right.append(splitFD[1])
    print 'left',left
    print 'right',right
    #we call closure in here
    closure_list = [attribute]
    closure(left, right, attribute, closure_list)
    close = eliminate_dupes(closure_list)
    print "C's closure: ", close
    
    return 

    
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
    #print "closure of c", close
    #print "all", closure_list
    
    k=1    
    while k < len(close):
        closure(l,r, close[k], closure_list) 
        k+=1
        

def eliminate_dupes(closure_list):
    one =  list(itertools.chain.from_iterable(closure_list))
    one = set(one)
    one = list(one)
    one = ''.join(one)
    return one
    
    
        
        
    
############################
#         MAIN             #
############################  
# spits the fd into 2 lists
L,R = connectDatabase()
print "LHS",L
print "RHS", R

getMinimalCover(L,R)




    

