"""This file loads the 10 csv files extracted from the Kaggle Formula 1 World Championship (1950 - 2024) dataset """

import csv
import os
from model import Driver, Team
from utils import safe_int, safe_float, is_null

class Dataloader:
  
  def __init__(self, data_dir="."):
      
        self.data_dir = data_dir
 
        self.drivers      = {}   # driverId(str)     
        self.teams        = {}   # constructorId(str)  
        self.races        = {}   # raceId(str)         
        self.status_map   = {}   # statusId(str)       
        self.season_final_races = set()   # raceId(str) of last race each year
 
    def _open_csv(self, filename):
        path = os.path.join(self.data_dir, filename)
        fh   = open(path, encoding="utf-8-sig", newline="")
        return csv.DictReader(fh)
 
 
    def load_status(self):
        """
        Build self.status_map: statusId(str) -> is_dnf (bool).
        CSV columns used: statusId, status
        """
        for row in self._open_csv("status.csv"):
            sid    = row["statusId"]
            status = row["status"].strip()
            # is_dnf = True if driver did NOT finish
            is_dnf = not (status == "Finished" or status.startswith("+"))
            self.status_map[sid] = is_dnf
 
        print(f"  Loaded {len(self.status_map)} status codes.")
 
    def load_races(self):
        """
        Build self.races (raceId -> year) and self.season_final_races.
        CSV columns used: raceId, year
        """
        year_to_max_race = {}   # year(str) -> max raceId(int)
 
        for row in self._open_csv("races.csv"):
            rid     = row["raceId"]
            year    = safe_int(row["year"], 0)
            self.races[rid] = {"year": year}
 
            rid_int = safe_int(rid)
            y_str   = row["year"]
            if y_str not in year_to_max_race or rid_int > year_to_max_race[y_str]:
                year_to_max_race[y_str] = rid_int
 
        self.season_final_races = {str(v) for v in year_to_max_race.values()}
        print(f"  Loaded {len(self.races)} races "
              f"({len(self.season_final_races)} season-final).")
 
    def load_drivers(self):
        """
        Create one Driver object per row in drivers.csv.
        CSV columns used: driverId, forename, surname, nationality, dob
        """
        for row in self._open_csv("drivers.csv"):
            did = row["driverId"]
            drv = Driver(
                driver_id   = did,
                forename    = row.get("forename",    "Unknown"),
                surname     = row.get("surname",     "Unknown"),
                nationality = row.get("nationality", "Unknown"),
                dob         = None if is_null(row.get("dob")) else row["dob"],
            )
            self.drivers[did] = drv
 
        print(f"  Loaded {len(self.drivers)} drivers.")
 
    def load_constructors(self):
        """
        Build Team objects from the unique constructorIds in results.csv.
        CSV columns used: constructorId (from results.csv)
        """
        cids = set()
        for row in self._open_csv("results.csv"):
            cids.add(row["constructorId"])
 
        for cid in cids:
            self.teams[cid] = Team(
                constructor_id = cid,
                name           = f"Constructor {cid}",
            )
        print(f"  Found {len(self.teams)} constructors.")
 
    def load_results(self):
        """
        Read results.csv and populate each Driver's raw accumulators.
        CSV columns used:
            raceId, driverId, constructorId, grid, positionOrder,
            points, statusId
        """
        rows_read = 0
        for row in self._open_csv("results.csv"):
            did = row["driverId"]
            cid = row["constructorId"]
            rid = row["raceId"]
 
            driver = self.drivers.get(did)
            if driver is None:
                continue
 
            grid_pos   = safe_int(row.get("grid",          "0"))
            finish_pos = safe_int(row.get("positionOrder", "0"))
            points     = safe_float(row.get("points",      "0"))
            status_id  = row.get("statusId", "1")
            is_dnf = self.status_map.get(status_id, False)
 
            driver.accumulate_results(grid_pos, finish_pos, points, is_dnf)
 
            race_year = self.races.get(rid, {}).get("year", 1950)
            if race_year < driver.debut_year or driver.debut_year == 1950:
                driver.debut_year = race_year
 
            team = self.teams.get(cid)
            if team:
                team.add_driver(driver)
 
            rows_read += 1
 
        print(f"  Processed {rows_read:,} result rows.")
 
    def load_sprint_results(self):
        """
        Add sprint race points from sprint_results.csv
        CSV columns used: driverId, points
        """
        rows_read = 0
        for row in self._open_csv("sprint_results.csv"):
            did    = row["driverId"]
            points = safe_float(row.get("points", "0"))
 
            driver = self.drivers.get(did)
            if driver is None:
                continue
 
            driver.accumulate_sprint(points)
            rows_read += 1
 
        print(f"  Processed {rows_read:,} sprint result rows.")
 
    def load_qualifying(self):
        """
        Add qualifying positions from qualifying.csv.
        CSV columns used: driverId, position
        """
        rows_read = 0
        for row in self._open_csv("qualifying.csv"):
            did       = row["driverId"]
            quali_pos = safe_int(row.get("position", "0"))
 
            driver = self.drivers.get(did)
            if driver is None:
                continue
 
            driver.accumulate_quali(quali_pos)
            rows_read += 1
 
        print(f"  Processed {rows_read:,} qualifying rows.")
 
    def load_driver_standings(self):
        """
        Count championship titles per driver using driver_standings.csv.
        CSV columns used: raceId, driverId, position
        """
        for row in self._open_csv("driver_standings.csv"):
            rid = row["raceId"]
            if rid not in self.season_final_races:
                continue              # skip mid-season standing rows
 
            position = safe_int(row.get("position", "99"))
            if position != 1:
                continue              # not the season champion
 
            did    = row["driverId"]
            driver = self.drivers.get(did)
            if driver:
                driver.championships += 1
 
        champs = sum(1 for d in self.drivers.values() if d.championships > 0)
        print(f"  Assigned championships to {champs} drivers.")
 
    def load_constructor_results(self):
        """
        Accumulate constructor championship points from
        constructor_results.csv.
        CSV columns used: constructorId, points
        """
        rows_read = 0
        for row in self._open_csv("constructor_results.csv"):
            cid    = row["constructorId"]
            points = safe_float(row.get("points", "0"))
 
            team = self.teams.get(cid)
            if team:
                team.accumulate_constructor_result(points)
            rows_read += 1
 
        print(f"  Processed {rows_read:,} constructor result rows.")
 
    def finalize(self):
        """
        Steps:
            1. For each Driver: compute_derived_stats()
               which internally calls build_feature_vector().
            2. For each Team: compute_team_vector().
        """
        active = 0
        for driver in self.drivers.values():
            driver.compute_derived_stats()
            if driver.races_started > 0:
                active += 1
 
        print(f"  Computed stats for {active:,} drivers with race data.")
 
        teams_done = 0
        for team in self.teams.values():
            team.compute_team_vector()
            if team.feature_vector:
                teams_done += 1
 
        print(f"  Computed vectors for {teams_done:,} teams.")
 
    def load_all(self):
        """
        Run every loading step in the mandatory order.
        """
        print("=" * 50)
        print("Loading F1 dataset (1950-2024)...")
        print("=" * 50)
        self.load_status()
        self.load_races()
        self.load_drivers()
        self.load_constructors()
        self.load_results()
        self.load_sprint_results()
        self.load_qualifying()
        self.load_driver_standings()
        self.load_constructor_results()
        self.finalize()
        print("=" * 50)
        print("Dataset ready.\n")
 
