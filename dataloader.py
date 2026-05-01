"""This file loads the 10 csv files extracted from the Kaggle Formula 1 World Championship (1950 - 2024) dataset """

import csv
import os
from class import Driver, Team
from utils import safe_int, safe_float, is_null

