"""This file contains driver and team classes"""

from utils import normalize_vector

class Driver:
    """represents an F1 driver and their career stats
        FEATURE VECTOR has 9 dimensions:
        [0] win_rate
        [1] podium_rate
        [2] self.normalized_points_per_race
        [3] avg_grid
        [4] dnf_rate
        [5] position_gain
        [6] avg_quali
        [7] championships
        """
    

# a weight to the points_per_race feature to account for the fact that modern seasons have 24 races while 1950s seasons only had 7
    
    POINTS_SYSTEM_MAP = {
    1950: 9.0,   # 1950s (8 or 9 pts for win)
    1960: 9.0,   
    1970: 9.0,   
    1980: 9.0,   
    1990: 10.0,  # 1990s (10 pts for win)
    2000: 10.0,  
    2010: 26.0,  # 2010s (25 pts + 1 for fastest lap)
    2020: 26.0   
}
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
        self.normalized_points_per_race = 0.0
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
        if 1 <= finish_pos <= 3: #fixed this previoulsy counted 0 as podium as well
            self.podiums += 1
        if is_dnf:
            self.dnfs += 1
        if finish_pos > 0:
            self.finish_sum += finish_pos
            self.finish_count += 1
        if grid_pos > 0:
            self.grid_sum   += grid_pos
            self.grid_count += 1

    def accumulate_quali(self, quali_pos):
        if quali_pos > 0:
            self.quali_sum += quali_pos
            self.quali_count += 1

    def accumulate_sprint(self, points):
        self.sprint_points += points

    def compute_derived_stats(self):
        """computes all rate based metrics with era adjustment"""
        r = self.races_started
        
        # Improvement: Drivers with fewer than 5 starts have volatile stats thatcan break the clustering. We skip building vectors for them.
        if r < 5:
            return 

        self.win_rate = self.wins / r
        self.podium_rate = self.podiums / r
        self.dnf_rate = self.dnfs / r

        # Calculate normalized points based on the era's max possible win points
        raw_points_per_race = (self.race_points + self.sprint_points) / r        
        decade = (self.debut_year // 10) * 10
        
        # FIXED: This now correctly looks up the decade (e.g., 1950 instead of 0)
        max_pts = self.POINTS_SYSTEM_MAP.get(decade, 26.0)
        self.normalized_points_per_race = raw_points_per_race / max_pts

        self.avg_grid = self.grid_sum / self.grid_count if self.grid_count > 0 else 0.0
        self.avg_quali = self.quali_sum / self.quali_count if self.quali_count > 0 else 0.0

        avg_finish = (self.finish_sum / self.finish_count if self.finish_count > 0 else 0.0)
        self.position_gain = self.avg_grid - avg_finish
 
        self.build_feature_vector()
    
    def build_feature_vector(self):
        
        # avg_quali is 0 for pre-1994 drivers (no qualifying data) — fall back to avg_grid
        quali = self.avg_quali if self.avg_quali > 0 else self.avg_grid

        # clamp normalized points to 1.0 — dominant drivers in long modern seasons
        # can exceed 1.0 if they score near-maximum points every race
        pts = min(self.normalized_points_per_race, 1.0)

        raw = [
            self.win_rate,              # [0] wins / races started
            self.podium_rate,           # [1] podiums / races started
            pts,                        # [2] normalized & clamped points per race
            self.avg_grid,              # [3] average starting position
            self.dnf_rate,              # [4] did-not-finish / races started
            self.position_gain,         # [5] mean(grid - finish), positive = overtaker
            quali,                      # [6] avg qualifying pos, falls back to avg_grid
            float(self.championships),  # [7] career world titles
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
 
