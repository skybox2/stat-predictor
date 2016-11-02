# Stat Predictor

Prediction engine for fantasy football player points. Utilizes the Stattleship API to get player and team defensive statistics. Utilizes sqlite to store roster and game_log information. Prediction tuning and lineup selection in progress. 

In Order to Create an updated nfl.db object, and populate it with Roster and Gamelog information: <br/>
**python stattleship_main.py roster** --> creates nfl.db and populates a roster table <br/>
**python stattleship_main.py populategl** --> creates and populates the gamelog table, full of all gamelog information for qb/rb/wr/te/defensive statistics


