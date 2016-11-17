import sqlite3

conn = sqlite3.connect('MiniProject2-InputExample.db')
c = conn.cursor()

def connectDatabase():

    # gives us table names
    c.execute("SELECT name FROM sqlite_master;")
    table_names = c.fetchall()
    print table_names
    
    # 1 list of the table names
    table = []
    for i in range(len(table_names)):
        for j in range(len(table_names[i])):
            table.append(str(table_names[i][j]))
    print table 
    
    # getting the column names
    c.execute("PRAGMA table_info(Input_R1)")
    col_names = c.fetchall()
    print col_names
    # This is the list of column names
    col= []
    for i in range (len(col_names)):
        col.append(str(col_names[i][1]))
    print col
            
        
   
connectDatabase()
    

