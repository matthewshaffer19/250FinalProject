#
# Authors: Matthew Shaffer and Luc Zbonack
# Description:
#   This code is designed to take in a csv file and draw conclusions about the data within it.
#

import sys
import os
import sqlite3
import math
import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.pyplot as plt
import numpy

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
    titles[0] = 'pk'

    #Connect to the DB
    conn = sqlite3.connect('extracted')

    #Use a loop to build a create statement
    create_statement = "CREATE TABLE IF NOT EXISTS " + table_name + "("
    for title in titles:
        temp = title.split('.')
        title = ''.join(temp)
        create_statement +=  title.strip('"') + " TEXT,"

    #Strip the final comma that we added with our loop
    create_statement = create_statement.rstrip(',')

    #Add the closing parenthesis for the statement
    create_statement += ")"

    #Execute the statement to create the table
    conn.execute(create_statement)
    
    #Populate the table by creating inserts for each line
    for line in f:
        #Make sure to replace the NA and FALSE and TRUE with no quotes to an NA and FALSE and TRUE with quotes or command will not be accepted as valid. This has to do with how Sqlite handles Booleans strangely
        line = line.replace("NA", '"NA"')
        line = line.replace("FALSE", '"FALSE"')
        line = line.replace("TRUE", '"TRUE"')
        #execute the insert statement
        conn.execute("INSERT INTO " + table_name + " VALUES (" + line +")")

    #Commit DB changes and close the file
    conn.commit()
    f.close()

#Create loop to run main body of the program in
while running == True:

    #Prompt user to select a data source for analysis
    print("INEX: Set data source:")
    
    #Make sure that the data source is valid and exists
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
    
    #Call the helper function to take the CSV and convert it into a SQL table
    extractor(dataSource)
    
    #Prompt user for what column(s) should be summarized
    print("INEX: What column(s) would you like to summarize?")
    
    tempString = sys.stdin.readline()

    #Analyze the string and slice it in a way that creates two variables that contain the column names
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
    
    #Make sure that the user gives a valid input when asked whether the plot should be text or graphical
    while valid != True:
        print("INEX: What type of plot should be generated? (text or graphical)")
    
        tempString = sys.stdin.readline().strip()
    
        if(tempString == "text" or tempString == "graphical"):
            plotType = tempString
            valid = True
        else: 
            valid = False


    #Connect to the database
    conn = sqlite3.connect('extracted')
    #Dynamically create the table name by removing the .csv from the end of the file that is the data source
    tableName = dataSource[:-4]
    
    #Generate the text plot
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
    
    #Generate the graphical plot
    if(plotType == "graphical"):
        #If the user has only asked for two columns to be summarized
        if(summarizeTwo != ""):
            #Run query to select every distinct entity from the column that the user has asked to summarize
            rowOneVals = conn.execute("SELECT DISTINCT " + summarizeOne + " FROM " + tableName + " ORDER BY " + summarizeOne).fetchall()
            #Create list to store processed values from row one
            rowTwoVals = []
            #Loop through every distinct value that the inital query found
            for val in rowOneVals:
                #Execute a new query that averages the values associated with each distinct value
                valToPrint = conn.execute("SELECT AVG(" + summarizeTwo + ")" + " FROM " + tableName + " WHERE " + summarizeOne + " LIKE '" + val[0] + "' ;")
                #Take all the queries we just processed and move them intoi clean list
                for val2 in valToPrint:
                    rowTwoVals.append(val2[0])

            #Create another new list for further cleaning of output
            cleanRowOneVals = []

            #Add all the results that our initially query found but strip them of characters that we do not want
            for i in rowOneVals:
                cleanRowOneVals.append(str(i).strip('''' (),' '''))

            #Convert the cleaned input to a tuple
            cleanRowOneVals = tuple(cleanRowOneVals)

            #Do what Ben told us to do
            bar_coords = numpy.arange(len(cleanRowOneVals))

            #Create the bar graph. Give the data and parameters that we want
            plt.bar(bar_coords, rowTwoVals, align='center', alpha=1.0, tick_label=cleanRowOneVals)

            #Label the axis
            plt.ylabel(summarizeTwo)
            plt.xlabel(summarizeOne)

            #Display the chart
            plt.show()
        #If the user has asked for one column to be summarized
        else:
            #Run query to select every distinct entity from the column that the user has asked to summarize
            rowOneVals = conn.execute("SELECT DISTINCT " + summarizeOne + " FROM " + tableName  + " ORDER BY " + summarizeOne).fetchall()
            #Create list to store values from the second desired summarized row
            rowTwoVals = []
            #Loop through every distinct value that the inital query found
            for val in rowOneVals:
                #Execute a new query that averages the values associated with each distinct value
                valToPrint = conn.execute("SELECT COUNT(" + summarizeOne + ")" + " FROM " + tableName + " WHERE " + summarizeOne + " LIKE '" + val[0] + "' ;")
                #Take all the queries we just processed and move them intoi clean list
                for val2 in valToPrint:
                    rowTwoVals.append(val2[0])
            
            #Create another new list for further cleaning of output
            cleanRowOneVals = []
            
            #Add all the results that our initially query found but strip them of characters that we do not want
            for i in rowOneVals:
                cleanRowOneVals.append(str(i).strip('''' (),' '''))

            #Convert the cleaned input to a tuple
            cleanRowOneVals = tuple(cleanRowOneVals)

            #Do what Ben told us to do
            bar_coords = numpy.arange(len(cleanRowOneVals))

            #Create the bar graph. Give the data and parameters that we want
            plt.bar(bar_coords, rowTwoVals, align='center', alpha=1.0, tick_label=cleanRowOneVals)

            #Label the axis
            plt.ylabel('Quantity')
            plt.xlabel(summarizeOne)

            #Display the chart
            plt.show()

#Run a query to grab all tables in a database then loop through the results and drop all of them.
    all_tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in all_tables:
        conn.execute("DROP TABLE " + table[0])

    #Commit changes to the DB and then close the connections
    conn.commit()
    conn.close()
    
    running = False
