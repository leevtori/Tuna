import sqlite3
import itertools
from collections import OrderedDict

#global variables
conn = sqlite3.connect('MiniProject2-InputExample.db')
c = conn.cursor()

l_list=[] #list of sets [{'A','B','H'},{'A','B','H'},{'A'},{'C'}]
r_list=[] #list of strings ['A','B','C']

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

def getMinimalCover():
    #step 1: right hand side singleton
    getSingleton()
    
    #step 2: left hand side extraneous attributes
    step2(l, r)
    

def getSingleton():
    singleton = []
    for i in range(len(r_list)):
        if len(r_list[i])> 1:    
            for letter in range(len(r_list[i])):
                singleton.append(l_list[i]+'->'+r_list[i][letter])
        else:
            singleton.append(l_list[i]+'->'+r_list[i])
    print 'singleton LIST',singleton
    
    # turn into list of sets
    l_list = []
    #this is still a list of strings
    r_list =[]
    
    for i in range(len(singleton)):
        splitFD = singleton[i].split('->') 
        l_list.append(splitFD[0])
        r_list.append(splitFD[1])
    # turn l_list into a list of sets
    for j in range(len(l_list)):
        s = set()
        for letter in l_list[j]:
            s.add(letter)
        l_list[j] = s
        
    ##return newLeft, newRight
       
       
def step2():
    for j in range(len(l_list)):
        if len(l_list[j])>1:
            remove_redundancy(l_list[j], r_list[j])
            
    
        
def remove_redundancy(LHS, RHS):
    LHS_copy = set(LHS)
    i = l_list.index(LHS)
    
    for letter in LHS_copy:
        attribute = LHS_copy.difference(letter)
        closure = getClosure(attribute)
        print attribute,"closure: ", closure
        # save the closures, per attriute
        if RHS in closure:
            print "removed", letter
            LHS.remove(letter)
            print "remaining", LHS
            #replace attributes with reduced attributes
            l_list[i] = LHS
    print l_list
    #print "from remove_redundancy", closure
        
def getClosure(attribute):
    #get copies of l and r
    l_copy = list(l_list)
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
                closure_set.add(r_copy[f])
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

#def closure(l, r, attribute, closure_list):
    ##initialize closure to list with the attribute
    #close = [attribute]
    #for i in range(len(l)):
        #if attribute == l[i]:
            ##check if attribute already exists
            #for a in close:
                #if a== r[i]:
                    #continue
                #else:
                    #close.append(r[i])
    #closure_list.append(close)
    #print "closure of c", close
    #print "all", closure_list
    
    #k=1    
    #while k < len(close):
        #closure(l,r, close[k], closure_list) 
        #k+=1
        

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
connectDatabase()

getMinimalCover()
#l, r = getSingleton(L, R)

#s = {'A','H'}
#getClosure(s, l, r)










    

