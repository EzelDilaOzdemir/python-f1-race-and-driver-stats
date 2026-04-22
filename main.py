#DSA102 COMPUTER PROGRAMMING PROJECT

import csv
import math
import os 
import random 

#SECTION 1: HELPER FUNCTIONS 

def safe_int(value, default = 0):
    """safely converts any value to integer as the datasets use "//N" as a null
     and has empty strings for missing cells """
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default 
    
def safe_float(value, default = 0.0):
    """safely converts any value to float """
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default