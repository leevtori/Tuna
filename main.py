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
    step2(l, r) #manipulates l and r
    print 'l',l,'\nr',r
    
    #step 3:
    step3(l,r)
    

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
    #this is still a list
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
    for j in range(len(L_list)):
        if len(L_list[j])>1:
            remove_redundancy(L_list[j], R_list[j], L_list, R_list)
            print '\nl list removed redundancy ',L_list,'\n'
    #print '\nr list removed redundancy', R_list
    return L_list    
    
def step3(l_list, r_list):
    #removed redundant FDs
    for fd in l_list:
    #find closure of current FD (exclude current FD)
        l_copy = list(l_list)
        r_copy = list(r_list)
        index = l_list.index(fd)
        print "fd", index
        l_copy.remove(l_list[index])
        r_copy.remove(r_list[index])
        print 'L copy',l_copy
        print 'R copy', r_copy
        closure = getClosure(fd,l_copy, r_copy)
        print "closure of T-",fd,"->",r_list[index],closure
        #if RHS of FD is in the closure, then delete this FD because it's redundant
        print '@@@r list index', r_list[index],'\n'
        if r_list[index].issubset(closure):
            #update l and r list
            l_list = list(l_copy)
            r_list = list(r_copy)
            print "removed redundant FD", l_list, r_list
        
            
    
def remove_redundancy(LHS, RHS, l_list, r_list):
    LHS_copy = set(LHS)
    i = l_list.index(LHS)
    
    for letter in LHS_copy:
        attribute = LHS_copy.difference(letter)
        closure = getClosure(attribute, l_list, r_list)
        print attribute,"closure: ", closure
        # save the closures, per attriute
        if RHS.issubset(closure):
            print "removed", letter
            
            LHS.remove(letter)
            print "remaining", LHS
            l_list[i] = LHS
            
        

        
    #print "from remove_redundancy", closure
        
def getClosure(attribute, l_list, r_list):
    #get copies of l and r
    l_copy = l_list
    r_copy = list(r_list)
    # adds the clos
    closure_set = set()
    addtoset(attribute, closure_set)
             
    f = 0
    added=True
    while added == True:
        added = False        
        for f in range(len(l_copy)):
            #print "index", f
            #print "new closure", closure_set
            if r_copy[f] == '':
                continue
            elif l_copy[f].issubset(closure_set):
                #print "issubset"
                #print r_copy[f]
                #print r_copy
                ##closure_set.add(r_copy[f])
                addtoset(r_copy[f],closure_set)
                #print "added", closure_set
                r_copy[f]=''
                f+=1
                added = True
            else :
                #print "notsubset"
                f += 1
        #print closure_set
    #print attri,"closure: ", closure_set
    return closure_set
            
   
           
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
#l, r = getSingleton(L, R)

#s = {'A','H'}
#getClosure(s, l, r)










    

