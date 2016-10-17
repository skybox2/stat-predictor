from stattlepy import Stattleship
import sqlite3
from datetime import datetime, timedelta
import numpy as np


# Stattleship-SPECIFIC CONSTANTS
access_token = "d49525fb16260a10a902f32b33aaa172"
# NFL-SPECIFIC CONSTANTS
offensive_positions = ['QB', 'RB', 'WR', 'TE']
current_season = "nfl-2016-2017"

# This function builds the gamelog table, which contains record entries
# for all game performances in the past year for all players in the form:
# (player id, , , , , )
# The function essentially works by stepping through one year of dates and
# individually calling updateGameLog().
def populateGameLog():
	# Open DB connection and create gamelog table
	conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS gamelog (player_id text,
		player_slug text, date text, opponent_slug text, home_away text,
		points_scored integer) ''')
	conn.commit()
	# sql ='SET SESSION max_allowed_packet=500M'
	# c.execute(sql)
	# Starting with today, update the game log for each day and 
	# decrement pointer by one day. End when pointer points to today one 
	# year ago.
	curr, step = datetime.now(), timedelta(days=1)
	for i in range(366):
		log_records = updateGameLog(curr - i * step, conn)
		sql_stmt = "INSERT OR REPLACE INTO gamelog VALUES (?, ?, ?, ?, ?, ?)"
		c.executemany(sql_stmt, log_records)
		conn.commit()
	# Compute the number of records added to gamelogs
	c.execute("SELECT COUNT(*) FROM gamelog")
	num_records = c.fetchone()[0]
	print "There are " + str(num_records) + " records in the gamelog table."
	# Upon looping through all teams, close DBconnection
	conn.close()

# This function adds player logs for games that happened on 
# date - note that this function assumes that there is an existing
# gamelog table that has been populated with populateGameLog(), and
# that this function solely exists to incrementally add recent logs 
# to an existing log table.
def updateGameLog(date=datetime.now(), conn=None):
	# Generate cursor for database connection if c=None
	if not conn:
		conn = sqlite3.connect('nfl.db')
	c = conn.cursor()
	# Convert date (datetime) into string 'yyyy-mm-dd'
	strdate = date.strftime('%Y-%m-%d')
	# Query stattleship for NFL teams
	new_query = Stattleship()
	token = new_query.set_token(access_token)
	teams = new_query.ss_get_results(sport='football',league='nfl',ep='teams')
	# Construct dictionary of all team_ids and each matching team_slug
	team_ids = {item['id'] : item['slug'] for item in teams[0]['teams']}
	# log_records will contain all of the date's game logs to be inserted
	# into gamelog at end of for loop
	log_records = []
	# One D/ST record is entered into gamelog for each team that plays
	# on date. At the end of the for loop, each entry in 
	# defensive_teams is added to log_records before it is inserted
	# into gamelog
	defensive_teams = {}
	# Loop through all valid pages of game logs for a given day
	for index in range(1, 1000):
		# Query stattleship for a page of date's game logs
		page = new_query.ss_get_results(sport='football',league='nfl', \
		ep='game_logs', on=strdate, page=str(index))
		logs = page[0]['game_logs']
		# If there are no more logs to consider, then break
		if not logs:
			break
		players = page[0]['players']
		for curr in range(len(logs)):
			# These are the current log entry and its associated player
			curr_log, curr_player = logs[curr], players[curr]
			# Determine player id, slug, position, and team 
			[id, slug, pos, team_id] = [curr_player[key] for key \
			in ('id', 'slug', 'position_abbreviation', 'team_id')]
			# For fantasy point calculation purposes, we must determine
			# whether the player is an offensive player; if not, the player's
			# points must be summed with all other defensive players'
			# contributions
			isOffensive = (pos in offensive_positions)
			# Utilize helper function to calculate the player's fantasy points
			# scored in date's game, or their contribution to the team's D/ST
			# fantasy point total
			curr_points = calculateFantasyPoints(curr_log, isOffensive)
			# If the player is not offensive, add his contributions to the
			# running total of his team's defensive fantasy point total
			if not isOffensive:
				# If team_id is not already stored in defensive_teams,
				# instantiate the dictionary for team_id and populate its
				# opponent and home_away entries using current log
				if team_id not in defensive_teams:
					defensive_teams[team_id] = {'points': 0, 
					'opponent': team_ids[curr_log['opponent_id']], 
					'home_away': 'home' if curr_log['is_home_team'] else 'away'}
				defensive_teams[team_id]['points'] += curr_points
			# If the player is offensive, add his log record to log_records
			else:
				record = [id, slug, strdate, team_ids[curr_log['opponent_id']], \
				'home' if curr_log['is_home_team'] else 'away', curr_points]
				print record
				log_records += [record]
	# Now loop through each entry in defensive_teams and add a record to 
	# log_records for each D/ST for each team for each game played on date
	for dst in defensive_teams:
		defense = defensive_teams[dst]
		record = [dst, team_ids[dst], strdate, defense['opponent'], \
		defense['home_away'], defense['points']]
		print record
		log_records += [record]
	return log_records

def calculateFantasyPoints(log, isOffensive):
	if isOffensive:
		x_vector = np.array([
			log['passes_touchdowns'],
			log['passes_yards_gross'],
			int(log['passes_yards_gross'] >= 300),
			log['interceptions_total'],
			log['rushes_yards'],
			log['total_touchdowns'] - log['passes_touchdowns'],
			int(log['rushes_yards'] >= 100),
			log['receptions_yards'],
			log['receptions_total'],
			int(log['receptions_yards'] >= 100),
			log['fumbles_lost'],
			log['receiving_2pt_conversions_succeeded'] + \
			log['passing_2pt_conversions_succeeded'] + \
			log['rushing_2pt_conversions_succeeded']])
		w_vector = np.array([4., .04, 3., -1., 0.1, 6., 3., \
			0.1, 1., 3., -1., 2.])
		return np.dot(x_vector, w_vector)
	else:
		opp_score = log['opponent_score']
		x_vector = np.array([
			log['sacks_total'],
			log['interceptions_total'],
			log['fumbles_opposing_recovered'],
			log['kickoff_return_touchdowns'],
			log['punt_return_touchdowns'],
			#blocked punt or fg return td
			log['interceptions_touchdown'],
			log['safeties'],
			log['field_goals_blocked'],
			log['extra_points_made'],
			int(opp_score == 0),
			int(opp_score >= 1 and opp_score <= 6),
			int(opp_score >= 7 and opp_score <= 13),
			int(opp_score >= 14 and opp_score <= 20),
			int(opp_score >= 21 and opp_score <= 27),
			int(opp_score >= 28 and opp_score <= 34),
			int(opp_score >= 35)])
		w_vector = np.array([1., 2., 2., 6., 6., 6., 2., 2., \
			2., 10., 7., 4., 1., 0., -1., -4.])
		return np.dot(x_vector, w_vector)