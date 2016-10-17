import argparse
import gamelog_football
import roster_football
import extract_train

# Currently implemented options for command line argument
# usage
actions = {'roster': roster_football.populateRoster,
		  'gamelog': gamelog_football.ugl,
		  'populategl': gamelog_football.pgl,
		  'xmain': extract_train.main,
		  'xsql': extract_train.xsql
		  }

parser = argparse.ArgumentParser(description='Tell stat-predictor what you want to do.')
parser.add_argument('action', type=str, choices=actions.keys())
args = parser.parse_args()
actions[args.action]()