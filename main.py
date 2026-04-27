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

class Driver:
    """represents an F1 driver and their career stats
    FEATURE VECTOR has 9 dimensions:
        [0] win_rate
        [1] podium_rate
        [2] points_per_race
        [3] avg_grid
        [4] dnf_rate
        [5] position_gain
        [6] avg_quali
        [7] era_encoded
        [8] championships"""
ERA_MAP = {1950: 0, 1960: 1, 1970: 2, 1980: 3,
        1990: 4, 2000: 5, 2010: 6, 2020: 7
    }

def __init__(self, driver_id, forename, surname, nationality, dob = None):
    self.driver_id   = driver_id
    self.forename    = forename
    self.surname     = surname
    self.nationality = nationality
    self.dob         = dob
    self.debut_year  = 1950    
 
    self.races_started  = 0
    self.wins           = 0
    self.podiums        = 0
    self.race_points    = 0.0   
    self.sprint_points  = 0.0   
    self.dnfs           = 0
    self.grid_sum       = 0    
    self.grid_count     = 0    
    self.finish_sum     = 0     
    self.finish_count   = 0
    self.quali_sum      = 0     
    self.quali_count    = 0
    self.championships  = 0
 
    self.win_rate        = 0.0
    self.podium_rate     = 0.0
    self.points_per_race = 0.0
    self.avg_grid        = 0.0
    self.dnf_rate        = 0.0
    self.position_gain   = 0.0
    self.avg_quali       = 0.0

    self.tier_label = "Unranked"
    self.cluster_id = -1
    self.feature_vector = []

@property #used it to turn the method into a read only attribute
def full_name(self):
    return f"{self.forename} {self.surname}"

def accumulate_results(self, grid_pos, finish_pos, points, is_dnf):
    self.races_started += 1
    self.race_points += points

    if finish_pos == 1:
        self.wins += 1
    if finish_pos <= 3:
        self.podiums += 1
    if is_dnf:
        self.dnfs += 1
    if finish_pos > 0:
        self.finish_sum += finish_pos
        self.finish_count += 1

def accumulate_quali(self, quali_pos):
    if quali_pos > 0:
        self.quali_sum += quali_pos
        self.quali_count += 1

def accumulate_sprint(self, points):
    self.sprint_points += points

def compute_derived_stats(self):
    """computes all rate based metrics"""
    r = self.races_started
    if r == 0:
        return #driver has no race data 
    
    self.win_rate = self.wins / r
    self.podium_rate = self.podiums / r
    self.dnf_rate = self.dnfs / r

    total_points = self.race_points + self.sprint_points
    self.points_per_race = total_points / r

    self.avg_grid = self.grid_sum / self.grid_count if self.grid_count > 0 else 0.0
    self.avg_quali = self.quali_sum / self.quali_count if self.quali_count > 0 else 0.0

    avg_finish = (self.finish_sum / self.finish_count if self.finish_count > 0 else 0.0)
    self.position_gain = self.avg_grid - avg_finish
 
    self.build_feature_vector()

def encode_era(self):
    decade = (self.debut_year // 10) * 10
    return self.ERA_MAP.get(decade, 7)

def build_feature_vector(self):
    """
    Assemble and normalize the 9-dimensional feature vector.
    """
    raw = [
        self.win_rate,               
        self.podium_rate,            
        self.points_per_race,        
        self.avg_grid,              
        self.dnf_rate,             
        self.position_gain,       
        self.avg_quali,            
        float(self._encode_era()),  
        float(self.championships),  
        ]
    self.feature_vector = normalize_vector(raw)
 
def __repr__(self):
    return (
        f"Driver({self.full_name!r}, "
        f"races={self.races_started}, wins={self.wins}, "
        f"tier={self.tier_label!r})"
    )

#SECTION 3: TEAM CLASS

class Team:
    """represents an F1 constructor and aggeragates its drivers"""
    def __init__(self, constructor_id, name, nationality= None):
        self.constructor_id = constructor_id
        self.name = name
        self.nationality = nationality

        self.drivers = []
        self.feature_vector = []

        self.total_race_entries = 0
        self.total_points = 0   

    def add_driver(self, driver):
        """registers a driver with this team"""

        if not isinstance(driver, Driver):
            raise TypeError("Expected a Driver instance")
        if driver not in self.drivers:
            self.drivers.append(driver)

    def accumulate_constructor_result(self, points):
        self.total_race_entries += 1
        self.total_points       += points

    def compute_team_vector(self):
        """Compute the team feature vector as the mean of
        all drivers' feature vectors."""

        active = [d for d in self.drivers if d.feature_vector]
        if not active:
            self.feature_vector = []
            return
 
        dim    = len(active[0].feature_vector)
        summed = [0.0] * dim
 
        for driver in active:
            for i, val in enumerate(driver.feature_vector):
                summed[i] += val
 
        n = len(active)
        self.feature_vector = [s / n for s in summed]
 
    def __repr__(self):
        return (
            f"Team({self.name!r}, "
            f"drivers={len(self.drivers)}, "
            f"pts={self.total_points:.0f})"
        )
 

