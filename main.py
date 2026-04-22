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
    
def is_null(value):
    """return true when a value repsresents missing data"""
    if value is None:
        return True
    if isinstance(value, str) and (value.strip() == "" or value.strip().upper() == "//N"):
        return True
    else:
        return False

def normalize_vector(vec):
    """scale and normalize a list of floats
    FORMULA: 
        magnitude = sqrt(x1^2 + x2^2 + ... + xn^2)
        normalized_i = xi / magnitude
 
        Result: sqrt(sum of normalized_i^2) = 1"""
    magnitude = math.sqrt(sum(x**2 for x in vec))
    if magnitude == 0.0:
        return vec[:] #cannot divide by zero
    else:
        return [ x / magnitude for x in vec]

def euclidian_distance(vec_a, vec_b):
    """
    Straight-line distance between two equal-length vectors.
    FORMULA:
        d(a, b) = sqrt( sum_i (ai - bi)^2 )
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be of same length") #each dimension represents an F1 metric, so lengths of vectrs should be equal 
    else: 
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

def cosine_similarity(vec_a, vec_b):
    """Measure the angle between two vectors, ignoring their magnitudes.
 
    FORMULA:
        cos(theta) = (A . B) / (|A| x |B|)
        where  A . B  = sum ai * bi        (dot product)
               |A|    = sqrt(sum ai^2)     (L2 magnitude)
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must be of same length")
    else:
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        mag_a = math.sqrt(sum(a ** 2 for a in vec_a))
        mag_b = math.sqrt(sum(b ** 2 for b in vec_b))
        if mag_a == 0.0 or mag_b == 0.0:
            return 0.0 #cannot divide by zero
        return dot_product / (mag_a * mag_b)

#SECTION 2: DRIVER CLASS 