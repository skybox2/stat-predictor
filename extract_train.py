import sqlite3
from datetime import datetime, timedelta
import numpy as np


# Create feature vector for player using parameters defined in infoDict. 
# When you add a feature, you must add: (1) an entry in infoDict, (2) a 
# function used to calculate it, and (3) a line in featureVector() to add
# the feature to the return vector. Return an np array of all features.
def featureVector(player, infoDict):
	result = []
	# ADD: Average over past year
	result += [yearAverageFeature(player, infoDict)]
	# ADD: Average over 5 most recent games
	result += [rollingAverageFeature(player, infoDict)]
	# ADD: Average over season vs. opponent
	result += [opponentAverageFeature(player, infoDict)]
	# ADD: Average over season when home/away
	result += [homeAwayAverageFeature(player, infoDict)]
	# Add features below
	return np.array(result)


# Average for player over past year since infoDict['date']
def yearAverageFeature(player, infoDict):
	# Get string format of today and one year back for SQLite querying
	# purposes
	start, end = infoDict['date'], infoDict['date'] - timedelta(days=365)
	strStart, strEnd = start.strftime('%Y%m%d'), end.strftime('%Y%m%d') 
	# Open DB connection
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	# Query gamelog for average points scored by player over past year
	sqlStmt = "SELECT AVG(points_scored) FROM gamelog WHERE player_slug=\"" + player
	sqlStmt += "\" AND date BETWEEN " + strEnd + " AND " + strStart
	c.execute(sqlStmt)
	# Return query results
	result = c.fetchone()[0]
	conn.close()
	return result

# Average for player over 5 most recent games since infoDict['date']
def rollingAverageFeature(player, infoDict):
	# Get string format of date for SQLite querying purposes
	strDate = infoDict['date'].strftime('%Y%m%d')
	# Open DB connection
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	# Query gamelog for average points scored by player over 5 most recent games
	# since date
	sqlStmt = "SELECT AVG(points_scored) FROM gamelog WHERE player_slug=\"" + player
	sqlStmt += "\" AND date  <=" + strDate + " ORDER BY date DESC LIMIT 5"
	c.execute(sqlStmt)
	# Return query results
	result = c.fetchone()[0]
	conn.close()
	return result

# Average for player against infoDict['opponent']
def opponentAverageFeature(player, infoDict):
	# Get opponent for SQLite querying purposes
	opponent = infoDict['opponent']
	# Open DB connection
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	# Query gamelog for average points scored by player against opponent
	sqlStmt = "SELECT AVG(points_scored) FROM gamelog WHERE player_slug=\"" + player
	sqlStmt += "\" AND opponent_slug = \"" + opponent + "\""
	c.execute(sqlStmt)
	# Return query results
	result = c.fetchone()[0]
	conn.close()
	return result
	

# Average for player when infoDict['home_away']
def homeAwayAverageFeature(player, infoDict):
	# Get home/away for SQLite querying purposes
	homeAway = infoDict['home_away']
	# Open DB connection
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	# Query gamelog for average points scored by player when home/away
	sqlStmt = "SELECT AVG(points_scored) FROM gamelog WHERE player_slug=\"" + player
	sqlStmt += "\" AND home_away = \"" + homeAway + "\""
	c.execute(sqlStmt)
	# Return query results
	result = c.fetchone()[0]
	conn.close()
	return result

# Some simple tests
def main():
	# slug for player
	player = 'nfl-cam-newton'
	infoDict = {'date': datetime.now(), 'opponent': 'nfl-den', 'home_away': 'home'}
	print featureVector(player, infoDict)

# For command line access to SQLite3 table
def sqlInteract():
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	while True:
		sqlStmt = raw_input("enter SQL code which you would like to run:  ")
		c.execute(sqlStmt)
		result = c.fetchall()
		print result

xsql = sqlInteract
	