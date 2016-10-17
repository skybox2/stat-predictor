import sys
import gamelog_football
import roster_football

# Check to make sure that only one command line argument
# has been passed in to the main file 
assert len(sys.argv) == 2

if sys.argv[1] == "populateRoster":
	roster_football.populateRoster()
elif sys.argv[1] == "populateGameLog":
	gamelog_football.populateGameLog()
elif sys.argv[1] == "updateGameLog":
	gamelog_football.updateGameLog()
else:
	print "Error: Invalid command line argument: "
	print "Please run: \"python stattleship_main.py <method>\""
	print "<method> = {populateRoster, populateGameLog, updateGameLog}"
