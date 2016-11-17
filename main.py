import sqlite3

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
    redudancy('C', singleton)
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
    closure(left, right, fd, attribute)
    return 

    
def closure(l, r, fd, attibute):
    
    #base case: find any fds that start with this attribute
    closure = [attribute]
    for i in range(len(l)):
        if attribute == l[i]:
            #check if attribute already exists
            for a in closure:
                if a== r[i]:
                    continue
                else:
                    closure.append(r[i])
    
    print "closure of c", closure
    
############################
#         MAIN             #
############################   
L,R = connectDatabase()
print "LHS",L
print "RHS", R

getMinimalCover(L,R)




    

