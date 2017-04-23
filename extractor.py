import sqlite3

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
	create_statement = "CREATE TABLE " + table_name + "("
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
		
extractor('diamond.csv')
