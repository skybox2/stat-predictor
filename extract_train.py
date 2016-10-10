import sqlite3
from datetime import datetime, timedelta
import numpy as np

def featureVector(player, info_dict):
	return np.array([1,1,1,1])