import sqlite3
import itertools
import fnmatch
from collections import OrderedDict
from itertools import chain, combinations
import re



def getRelationalSchema(relation):
    table_name = 'Input_R'+relation
    print table_name
    
    ## GET COLUMN NAMES
    #sql = "PRAGMA table_info("+table_name+");"
    #c.execute(sql)
    #col_names = c.fetchall()
    #print col_names
    
    ## This is the list of column names
    #col= []
    #for i in range (len(col_names)):
        #col.append(str(col_names[i][1]))
    ##print 'Columns of R'+relation,col

    ## GET FUNCTIONAL DEPENDENCIES
    ## get LHS
    #table_fds = 'Input_FDs_R'+relation
    #sql = "select LHS from "+table_fds+";"
    #c.execute(sql)
    #lhs = c.fetchall()
    #LHS = []
    #for i in range(len(lhs)):
        #for j in range(len(lhs[i])):
            #LHS.append(''.join(str(lhs[i][j]).split(',')))
    ##get RHS
    #sql = "select RHS from "+table_fds+";"
    #c.execute(sql)
    #rhs = c.fetchall()
    #RHS = []
    #for i in range(len(rhs)):
        #for j in range(len(rhs[i])):
            #RHS.append(''.join(str(rhs[i][j]).split(',')))

    #return LHS,RHS, col

################ MAIN ##########################
conn = sqlite3.connect('MiniProject2-InputExample.db')

c = conn.cursor()

lhs, rhs, col = getRelationalSchema(1)