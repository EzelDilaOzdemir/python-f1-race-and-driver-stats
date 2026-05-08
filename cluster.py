import random 

TIER_LABELS = ["GOAT", "Legendary", "Race Winner", "Point Scorer", "Backmarker"]
 
    def __init__(self, k=5, max_iterations=300, random_seed=42):
        self.k              = k
        self.max_iterations = max_iterations
        random.seed(random_seed)
 
        self.centroids = []    # list of k feature vectors (lists of float)
        self.clusters  = {}    # cluster_id(int) -> list of Driver
        self.drivers   = []    # Driver objects passed to fit()
 
    def fit(self, drivers):
        """
        Run K-Means on *drivers* and assign tier_label to each driver.
        """
        self.drivers = [d for d in drivers if d.feature_vector]
 
        if len(self.drivers) < self.k:
            raise ValueError(
                f"Cannot form {self.k} clusters from "
                f"{len(self.drivers)} drivers."
            )
 
        print(f"Running K-Means (k={self.k}) on "
              f"{len(self.drivers):,} drivers...")
 

        self.centroids = self._kmeans_plus_plus_init()
 
        for iteration in range(1, self.max_iterations + 1):
            new_assignments = self._assign_clusters()
            changed         = self._update_centroids(new_assignments)
            if not changed:
                print(f"  Converged after {iteration} iteration(s).")
                break
        else:
            print(f"  Stopped at max iterations ({self.max_iterations}).")
 
        self._assign_tier_labels()
        return self
 
    def find_similar_drivers(self, target, top_n=5, metric="cosine"):
        """
        Return the *top_n* drivers most similar to *target*.
        """
        if not target.feature_vector:
            raise ValueError(f"{target.full_name} has no feature vector.")
 
        scores = []
        for driver in self.drivers:
            if driver.driver_id == target.driver_id:
                continue
 
            if metric == "cosine":
                score = cosine_similarity(
                    target.feature_vector, driver.feature_vector
                )
            elif metric == "euclidean":
                # Negate so that "higher = better" convention holds
                score = -euclidean_distance(
                    target.feature_vector, driver.feature_vector
                )
            else:
                raise ValueError(f"Unknown metric: {metric!r}")
 
            scores.append((driver, score))
 
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]
 
    def get_cluster_summary(self):
        """
        Return per-tier statistics as a nested dictionary
        """
        summary = {}
        for cid, members in self.clusters.items():
            if not members:
                continue
            label      = members[0].tier_label
            n          = len(members)
            avg_win    = sum(d.win_rate    for d in members) / n
            avg_podium = sum(d.podium_rate for d in members) / n
            top        = sorted(members, key=lambda d: d.wins, reverse=True)[:5]
            summary[label] = {
                "driver_count"    : n,
                "avg_win_rate"    : round(avg_win,    4),
                "avg_podium_rate" : round(avg_podium, 4),
                "top_drivers"     : [d.full_name for d in top],
            }
        return summary
 
 
    def _kmeans_plus_plus_init(self):
        vectors   = [d.feature_vector for d in self.drivers]
        # First centroid: uniformly random
        centroids = [vectors[random.randrange(len(vectors))][:]]
 
        for _ in range(self.k - 1):
            # D^2 for each point to its nearest already-chosen centroid
            d_squared = []
            for vec in vectors:
                min_d2 = min(
                    euclidean_distance(vec, c) ** 2
                    for c in centroids
                )
                d_squared.append(min_d2)
 
            # Weighted random selection proportional to D^2
            total = sum(d_squared)
            if total == 0:
                idx = random.randrange(len(vectors))
            else:
                threshold  = random.uniform(0, total)
                cumulative = 0.0
                idx        = 0
                for i, ds in enumerate(d_squared):
                    cumulative += ds
                    if cumulative >= threshold:
                        idx = i
                        break
 
            centroids.append(vectors[idx][:])   # copy, not reference
 
        return centroids
 
    def _assign_clusters(self):
        """
        Assign each driver to the nearest centroid.
        """
        new_clusters = {i: [] for i in range(self.k)}
 
        for driver in self.drivers:
            distances = [
                euclidean_distance(driver.feature_vector, c)
                for c in self.centroids
            ]
            nearest           = distances.index(min(distances))
            driver.cluster_id = nearest
            new_clusters[nearest].append(driver)
 
        self.clusters = new_clusters
        return new_clusters
 
    def _update_centroids(self, new_clusters):
        dim     = len(self.centroids[0])
        changed = False
 
        for i in range(self.k):
            members = new_clusters.get(i, [])
 
            if not members:
                new_c = random.choice(self.drivers).feature_vector[:]
                if new_c != self.centroids[i]:
                    self.centroids[i] = new_c
                    changed = True
                continue
 
            # Element-wise sum across all member vectors
            new_c = [0.0] * dim
            for driver in members:
                for j, v in enumerate(driver.feature_vector):
                    new_c[j] += v
            # Divide by member count to get the mean
            new_c = [s / len(members) for s in new_c]
 
            # Check if the centroid moved more than floating-point noise
            if euclidean_distance(new_c, self.centroids[i]) > 1e-9:
                changed = True
 
            self.centroids[i] = new_c
 
        return changed
 
    def _assign_tier_labels(self):
        def quality(cid):
            members = self.clusters.get(cid, [])
            if not members:
                return 0.0
            n = len(members)
            return (
                sum(d.win_rate        for d in members) / n * 3 +
                sum(d.podium_rate     for d in members) / n * 2 +
                sum(d.points_per_race for d in members) / n
            )
 
        ranked = sorted(self.clusters.keys(), key=quality, reverse=True)
 
        for rank, cid in enumerate(ranked):
            label = (self.TIER_LABELS[rank]
                     if rank < len(self.TIER_LABELS)
                     else f"Tier {rank + 1}")
            for driver in self.clusters.get(cid, []):
                driver.tier_label = label
 
 
