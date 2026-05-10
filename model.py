from utils import normalize_vector

class Driver:
    # FIXED: Updated keys to 4-digit years to match decade logic
    POINTS_SYSTEM_MAP = {
        1950: 9.0, 1960: 9.0, 1970: 9.0, 1980: 9.0,
        1990: 10.0, 2000: 10.0, 2010: 26.0, 2020: 26.0
    }

    def __init__(self, driver_id, forename, surname, nationality, dob=None):
        self.driver_id = driver_id
        self.forename = forename
        self.surname = surname
        self.nationality = nationality
        self.dob = dob
        self.debut_year = 1950
        self.races_started = 0
        self.wins = 0
        self.podiums = 0
        self.race_points = 0.0
        self.sprint_points = 0.0
        self.dnfs = 0
        self.grid_sum = 0
        self.grid_count = 0
        self.finish_sum = 0
        self.finish_count = 0
        self.quali_sum = 0
        self.quali_count = 0
        self.championships = 0
        self.win_rate = 0.0
        self.podium_rate = 0.0
        self.normalized_points_per_race = 0.0
        self.avg_grid = 0.0
        self.dnf_rate = 0.0
        self.position_gain = 0.0
        self.avg_quali = 0.0
        self.tier_label = "Unranked"
        self.feature_vector = []

    @property
    def full_name(self):
        return f"{self.forename} {self.surname}"

    def accumulate_results(self, grid_pos, finish_pos, points, is_dnf):
        self.races_started += 1
        self.race_points += points
        if finish_pos == 1: self.wins += 1
        if 1 <= finish_pos <= 3: self.podiums += 1
        if is_dnf: self.dnfs += 1
        if finish_pos > 0:
            self.finish_sum += finish_pos
            self.finish_count += 1
        if grid_pos > 0:
            self.grid_sum += grid_pos
            self.grid_count += 1

    def accumulate_quali(self, quali_pos):
        if quali_pos > 0:
            self.quali_sum += quali_pos
            self.quali_count += 1

    def accumulate_sprint(self, points):
        self.sprint_points += points

    def compute_derived_stats(self):
        r = self.races_started
        if r < 20: return # Filter low-sample drivers
        self.win_rate = self.wins / r
        self.podium_rate = self.podiums / r
        self.dnf_rate = self.dnfs / r
        raw_ppr = (self.race_points + self.sprint_points) / r
        decade = (self.debut_year // 10) * 10
        max_pts = self.POINTS_SYSTEM_MAP.get(decade, 26.0)
        self.normalized_points_per_race = raw_ppr / max_pts
        self.avg_grid = self.grid_sum / self.grid_count if self.grid_count > 0 else 0.0
        self.avg_quali = self.quali_sum / self.quali_count if self.quali_count > 0 else 0.0
        avg_finish = self.finish_sum / self.finish_count if self.finish_count > 0 else 0.0
        self.position_gain = self.avg_grid - avg_finish
        self.build_feature_vector()

    def build_feature_vector(self):
        quali = self.avg_quali if self.avg_quali > 0 else self.avg_grid
        pts = min(self.normalized_points_per_race, 1.0)
        raw = [self.win_rate, self.podium_rate, pts, self.avg_grid, self.dnf_rate, self.position_gain, quali, float(self.championships)]
        self.feature_vector = normalize_vector(raw)

class Team:
    def __init__(self, constructor_id, name, nationality=None):
        self.constructor_id = constructor_id
        self.name = name
        self.nationality = nationality
        self.drivers = []
        self.feature_vector = []
        self.total_points = 0

    def add_driver(self, driver):
        if driver not in self.drivers: self.drivers.append(driver)

    def accumulate_constructor_result(self, points):
        self.total_points += points

    def compute_team_vector(self):
        active = [d for d in self.drivers if d.feature_vector]
        if not active: return
        dim = len(active[0].feature_vector)
        summed = [0.0] * dim
        for d in active:
            for i, v in enumerate(d.feature_vector): summed[i] += v
        self.feature_vector = [s / len(active) for s in summed]
