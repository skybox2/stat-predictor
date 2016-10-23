# Stat Predictor

Prediction engine for fantasy football player points. Utilizes the Stattleship API to get player and team defensive statistics. Utilizes sqlite to store roster and game_log information. Prediction tuning and lineup selection in progress. 

*Supported Operations*: <br/>
**python stattleship_main.py roster** --> creates nfl.db and populates a roster table 
**python stattleship_main.py populategl** --> creates and populates the gamelog table, full of all gamelog information for qb/rb/wr/te/defensive statistics


