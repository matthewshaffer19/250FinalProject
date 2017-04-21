#
# Authors: Matthew Shaffer and Luc Zbonack
# Description:
#   This code is designed to take in a csv file and draw conclusions about the data within it.
#

import sys
import os

running = True

valid = False
toSummarize = []
plotType = ""

while running == True:
    
    print("INEX: Set data source:")
    
    while valid != True:
        valid = True
        tempString = "./" + sys.stdin.readline().strip()
        try:
            f = open(tempString, 'r')
            #f.close()
        except IOError as e:
            valid = False
            print("INEX: File not found, enter another:")          
        
    print("INEX: What column(s) would you like to summarize?")
    
    tempString = sys.stdin.readline()

    if("|" in tempString):
        stringsToAdd = tempString.split(" | ")
        toSummarize.append(stringsToAdd[0].strip())
        toSummarize.append(stringsToAdd[1].strip())
    else:
        toSummarize.append(tempString.strip())

    valid = False
    
    while valid != True:
        print("INEX: What type of plot should be generated? (text or graphical)")
    
        tempString = sys.stdin.readline().strip()
    
        if(tempString == "text" or tempString == "graphical"):
            plotType = tempString
            valid = True
        else: 
            valid = False
    
    running = False
