from stattlepy import Stattleship
import sqlite3
from datetime import datetime, timedelta
import numpy as np


# Stattleship-SPECIFIC CONSTANTS
access_token = "d49525fb16260a10a902f32b33aaa172"
# NFL-SPECIFIC CONSTANTS
offensive_positions = ['QB', 'RB', 'WR', 'TE']
current_season = "nfl-2016-2017"


# This function builds the roster table, which contains record entries
# for all current players of all teams in the form:
# (first name, last name, team slug, position, player slug, player id)
def populateRoster():
	# Query stattleship for NFL teams
	new_query = Stattleship()
	token = new_query.set_token(access_token)
	teams = new_query.ss_get_results(sport='football',league='nfl',ep='teams')
	# Construct dictionary of all team_slugs and each matching team_id
	team_slugs = {item['slug'] : item['id'] for item in teams[0]['teams']}
	# Open DB connection and create roster table
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS roster (first text, last text,
		team text, position text, player_slug text, player_id text PRIMARY KEY)''')
	conn.commit()
	# Loop through each team in team_slugs
	for team in team_slugs:
		# player_records will contain all of the team's player records to be inserted
		# into roster at end of for loop
		player_records = []
		# Want to look at all valid pages of players for a given team
		for index in range(1, 30):
			# Query stattleship for a page of team's roster
			page = new_query.ss_get_results(sport='football',league='nfl', \
			ep='players', team_id=team, season_id=current_season, page=str(index))
			page_of_players = page[0]['players']
			# If there are no more players to consider, move to next team
			if not page_of_players:
				break
			# Loop through each player on page
			for player in page_of_players:
				# If player should be considered, add his record to be inserted
				if player['position_abbreviation'] in offensive_positions:
					record = (player['first_name'], player['last_name'], \
						team, player['position_abbreviation'], player['slug'], \
						player['id'])
					player_records += [record]
		# Create one record for team's D/ST
		defense = (team, 'D/ST', team, 'D/ST', team, team_slugs[team])
		player_records += [defense]
		# Insert team's player records, commit
		sql_stmt = "INSERT OR REPLACE INTO roster VALUES (?, ?, ?, ?, ?, ?)"
		c.executemany(sql_stmt, player_records)
		conn.commit()
		print "Done with team " + team + ". "
	# Compute the number of records added within for loops
	c.execute("SELECT COUNT(*) FROM roster")
	num_records = c.fetchone()[0]
	print "There are " + str(num_records) + " records in the roster table."
	# Upon looping through all teams, close DBconnection
	conn.close()