import csv
import os
from model import Driver, Team
from utils import safe_int, safe_float, is_null

class DataLoader:
    def __init__(self, data_dir="."):
        self.data_dir = data_dir
        self.drivers = {}
        self.teams = {}
        self.races = {}
        self.status_map = {}
        self.season_final_races = set()

    def _open_csv(self, filename):
        path = os.path.join(self.data_dir, filename)
        return csv.DictReader(open(path, encoding="utf-8-sig", newline=""))

    def load_status(self):
        for row in self._open_csv("status.csv"):
            sid = row["statusId"]
            status = row["status"].strip()
            self.status_map[sid] = not (status == "Finished" or status.startswith("+"))

    def load_races(self):
        year_to_max_race = {}
        for row in self._open_csv("races.csv"):
            rid = row["raceId"]
            year = safe_int(row["year"], 0)
            self.races[rid] = {"year": year}
            if str(year) not in year_to_max_race or safe_int(rid) > year_to_max_race[str(year)]:
                year_to_max_race[str(year)] = safe_int(rid)
        self.season_final_races = {str(v) for v in year_to_max_race.values()}

    def load_drivers(self):
        for row in self._open_csv("drivers.csv"):
            did = row["driverId"]
            self.drivers[did] = Driver(did, row.get("forename", "Unknown"), row.get("surname", "Unknown"), row.get("nationality", "Unknown"), row.get("dob"))

    def load_constructors(self):
        for row in self._open_csv("results.csv"):
            cid = row["constructorId"]
            if cid not in self.teams:
                self.teams[cid] = Team(cid, f"Constructor {cid}")

    def load_results(self):
        for row in self._open_csv("results.csv"):
            driver = self.drivers.get(row["driverId"])
            if not driver: continue
            driver.accumulate_results(safe_int(row["grid"]), safe_int(row["positionOrder"]), safe_float(row["points"]), self.status_map.get(row["statusId"], False))
            year = self.races.get(row["raceId"], {}).get("year", 1950)
            if year < driver.debut_year or driver.debut_year == 1950: driver.debut_year = year
            team = self.teams.get(row["constructorId"])
            if team: team.add_driver(driver)

    def load_all(self):
        print("Loading F1 dataset...")
        self.load_status()
        self.load_races()
        self.load_drivers()
        self.load_constructors()
        self.load_results()
        for d in self.drivers.values(): d.compute_derived_stats()
        for t in self.teams.values(): t.compute_team_vector()
        print("Dataset ready.")
