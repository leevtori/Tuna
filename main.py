import sqlite3
import itertools
import fnmatch
from collections import OrderedDict
from itertools import chain
import re


conn = sqlite3.connect('MiniProject2-InputExample.db')
c = conn.cursor()

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
    print 'Columns of R'+relation,col

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

def getMinimalCover(left, right):
    #step 1: right hand side singleton
    l, r = getSingleton(left, right)
    
    #step 2: left hand side extraneous attributes
    step2(l, r) #manipulates l and r
    #print 'l',l,'\nr',r
    
    #step 3: Remove redundant FD's
    rl,rr = step3(l,r)
    left, right = convert_to_list(rl, rr)
    
    # Combine into functional dependancies, and return the minimal cover FD
    minimal_FD = []
    for i in range(len(left)):
        minimal_FD.append(left[i]+'->'+right[i])

    print 'Minimal Cover', minimal_FD, '\n' 
    return minimal_FD
   
# converts the reduced list of sets into list of lists
def convert_to_list(rl, rr):
    left = []
    right = []
    for items in rl:
        #change type 
        l = list(items)
        left.append(l)   
    for i in rr:
        r = list(i)
        right.append(r)
    l = []
    for item in left:
        x=''.join(item)
        l.append(x)
    right =list(chain.from_iterable(right))
    return l, right


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
       
       
def step2(L_list, R_list):
    for j in range(len(L_list)):
        if len(L_list[j])>1:
            remove_redundancy(L_list[j], R_list[j], L_list, R_list)
            #print '\nl list removed redundancy ',L_list,'\n'
    #print '\nr list removed redundancy', R_list
    return L_list    
    
def step3(l_list, r_list):
    reduced_l_list = []
    reduced_r_list = []
    #removed redundant FDs
    for i in range(len(l_list)):
    #find closure of current FD (exclude current FD)
        l_copy = list(l_list)
        r_copy = list(r_list)
        l_copy.remove(l_list[i])
        r_copy.remove(r_list[i])
        closure = getClosure(l_list[i],l_copy, r_copy)
        #print "closure of T-",fd,"->",r_list[index],closure
        #if RHS of FD is not in the closure, then this FD is not redundant, add it to reduced lists
        if not r_list[i].issubset(closure):
            reduced_l_list.append(l_list[i])
            reduced_r_list.append(r_list[i])
            #print "** reduced fd list", reduced_l_list
            #print "** reduced fd list", reduced_r_list
    return reduced_l_list, reduced_r_list          
    
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
                addtoset(r_copy[f],closure_set)
                #print "added", closure_set
                r_copy[f]=''
                f+=1
                added = True
            else :
                #print "notsubset"
                f += 1
        #print closure_set
    #print attribute,"closure: ", closure_set
    return closure_set
                  
def addtoset(set1,set2):
    for letter in set1:
        set2.add(letter)
        
        

#==============================================================================#
# check_3nf(LH, RH, F)
# checks if F is in 3nf. First checks if F is in BCNF. If yes, the function will
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
    print sql
    drop = "DROP VIEW IF EXISTS "+name

    c.execute(drop)
    c.execute(sql)    

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
    print sql
    drop = "DROP VIEW IF EXISTS "+name
  
    c.execute(drop)
    c.execute(sql)     
              
                            
############################
#         MAIN             #
############################  

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

# prompt user to pick a relation
relation = raw_input('Pick a table by entering its number: ')

# spits the fd into 2 lists
L,R = getRelationalSchema(relation)

#get minimal cover of FDs
#getMinimalCover(L,R)
TNF, LH, RH = third_normal(L, R)

output_schema(LH, RH, relation)
output_FD(LH, RH, relation) 

print








    

