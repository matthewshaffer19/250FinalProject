#
# Authors: Matthew Shaffer and Luc Zbonack
# Description:
#   This code is designed to take in a csv file and draw conclusions about the data within it.
#

import sys
import os
import sqlite3
import math

running = True

valid = False
toSummarize = []
summarizeOne = ""
summarizeTwo = ""
plotType = ""
dataSource = ""

def extractor(file):
	#Remove .csv from end of filename so we have a nice name for our table
	table_name = file[:-4]
	#Open the file
	f = open(file, 'r')
	#Grab the first line and split it on commas to get each atribute for the table we build
	titles = f.readline().strip().split(',')
	#Change the first element from an empty string to PK referencing Primary Key (This may not be necessay but it makes it cleaner IMO)
	titles[0] = 'PK'

	#Connect the the DB
	conn = sqlite3.connect('extracted')

	#Use a loop to build a create statement
	create_statement = "CREATE TABLE IF NOT EXISTS " + table_name + "("
	for title in titles:
		create_statement +=  title.strip('"') + " TEXT,"

	#Strip the final comma that we added with our loop
	create_statement = create_statement.rstrip(',')

	#Add the closing parenthesis for the statement
	create_statement += ")"

	#Execute the statement to create the table
	conn.execute(create_statement)
	
	#Populate the table by creating inserts for each line
	for line in f:
		#Make sure to replace the NA with no quotes to an NA with quotes or command will not be accepted as valid
		line = line.replace("NA", '"NA"')
		#execute the insert statement
		conn.execute("INSERT INTO " + table_name + " VALUES (" + line +")")

	#Commit DB changes and close the file
	conn.commit()
	f.close()

while running == True:
    
    print("INEX: Set data source:")
    
    while valid != True:
        valid = True
        dataSource = sys.stdin.readline().strip()
        tempString = "./" + dataSource
        try:
            f = open(tempString, 'r')
            #f.close()
        except IOError as e:
            valid = False
            print("INEX: File not found, enter another:")          
    
    extractor(dataSource)
    
    print("INEX: What column(s) would you like to summarize?")
    
    tempString = sys.stdin.readline()

    if("|" in tempString):
        stringsToAdd = tempString.split(" | ")
        toSummarize.append(stringsToAdd[0].strip())
        summarizeOne = stringsToAdd[0].strip()
        toSummarize.append(stringsToAdd[1].strip())
        summarizeTwo = stringsToAdd[1].strip()
    else:
        toSummarize.append(tempString.strip())
        summarizeOne = tempString.strip()

    valid = False
    
    while valid != True:
        print("INEX: What type of plot should be generated? (text or graphical)")
    
        tempString = sys.stdin.readline().strip()
    
        if(tempString == "text" or tempString == "graphical"):
            plotType = tempString
            valid = True
        else: 
            valid = False
    
    conn = sqlite3.connect('extracted')
    tableName = dataSource[:-4]
    
    
    
    if(plotType == "text"):
        if(summarizeTwo != ""):
            frontSpace = int((33 - len(summarizeTwo)) / 2)
            backSpace = 33 - len(summarizeTwo) - frontSpace
            print("---------------------------------------------")
            print("|" + " " * (7 - len(summarizeOne)) + summarizeOne + "  |" + " " * frontSpace + summarizeTwo + " " * backSpace + "|")
            print("|-------------------------------------------|")
            rowOneVals = conn.execute("SELECT DISTINCT " + summarizeOne + " FROM " + tableName + " ORDER BY " + summarizeOne + ";" ).fetchall()
            rowTwoVals = []
            counter = 0
            for val in rowOneVals:
                valToPrint = conn.execute("SELECT AVG(" + summarizeTwo + ")" + " FROM " + tableName + " WHERE " + summarizeOne + " LIKE '" + val[0] + "' ;")
                for val2 in valToPrint:
                    rowTwoVals.append(val2[0])
                #print(val[0])
                counter += 1
            multiplier = 32 / max(rowTwoVals)
            counter = 0
            for val in rowOneVals:
                valPounds = math.ceil(multiplier * rowTwoVals[counter])
                valSpaces = 32 - valPounds
                print("|" + " " * (7 - len(val[0])) + val[0] + "  | " + "#" * valPounds + " " * valSpaces + "|")
                counter += 1
            print("---------------------------------------------")
        else:
            print("---------------------------------------------")
            print("|" + " " * (7 - len(summarizeOne)) + summarizeOne + "  |                                 |")
            print("|-------------------------------------------|")
            rowOneVals = conn.execute("SELECT DISTINCT " + summarizeOne + " FROM " + tableName + " ORDER BY " + summarizeOne + ";" ).fetchall()
            rowTwoVals = []
            counter = 0
            for val in rowOneVals:
                valToPrint = conn.execute("SELECT COUNT(" + summarizeOne + ")" + " FROM " + tableName + " WHERE " + summarizeOne + " LIKE '" + val[0] + "' ;")
                for val2 in valToPrint:
                    rowTwoVals.append(val2[0])
                #print(val[0])
                counter += 1
            multiplier = 32 / max(rowTwoVals)
            counter = 0
            for val in rowOneVals:
                valPounds = int(multiplier * rowTwoVals[counter])
                valSpaces = 32 - valPounds
                print("|" + " " * (7 - len(val[0])) + val[0] + "  | " + "#" * valPounds + " " * valSpaces + "|")
                counter += 1
            print("---------------------------------------------")
    
    if(plotType == "graphical"):
        if(summarizeTwo != ""):
            print("graphical")
        #else:
    
    conn.execute("DROP TABLE d;")
    conn.commit()
    conn.close()
    
    running = False

    
    

