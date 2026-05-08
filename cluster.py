import random
from utils import euclidean_distance, cosine_similarity

class ClusterManager:
    TIER_LABELS = ["GOAT", "Legendary", "Race Winner", "Point Scorer", "Backmarker"]

    def __init__(self, k=5, max_iterations=300, random_seed=42):
        self.k = k
        self.max_iterations = max_iterations
        random.seed(random_seed)
        self.centroids = []
        self.clusters = {}
        self.drivers = []

    def fit(self, drivers):
        self.drivers = [d for d in drivers if d.feature_vector]
        if len(self.drivers) < self.k: raise ValueError("Not enough drivers for clusters.")
        self.centroids = self._kmeans_plus_plus_init()
        for i in range(self.max_iterations):
            new_assignments = self._assign_clusters()
            if not self._update_centroids(new_assignments): break
        self._assign_tier_labels()

    def _kmeans_plus_plus_init(self):
        vectors = [d.feature_vector for d in self.drivers]
        centroids = [random.choice(vectors)[:]]
        for _ in range(self.k - 1):
            d2 = [min(euclidean_distance(v, c)**2 for c in centroids) for v in vectors]
            centroids.append(vectors[random.choices(range(len(vectors)), weights=d2)[0]][:])
        return centroids

    def _assign_clusters(self):
        new_clusters = {i: [] for i in range(self.k)}
        for d in self.drivers:
            dist = [euclidean_distance(d.feature_vector, c) for c in self.centroids]
            idx = dist.index(min(dist))
            new_clusters[idx].append(d)
        self.clusters = new_clusters
        return new_clusters

    def _update_centroids(self, new_clusters):
        changed = False
        for i in range(self.k):
            members = new_clusters[i]
            if not members: continue
            new_c = [sum(d.feature_vector[j] for d in members)/len(members) for j in range(len(self.centroids[0]))]
            if euclidean_distance(new_c, self.centroids[i]) > 1e-9:
                self.centroids[i], changed = new_c, True
        return changed

    def _assign_tier_labels(self):
        def quality(cid):
            members = self.clusters.get(cid, [])
            if not members: return 0.0
            n = len(members)
            return (sum(d.win_rate for d in members) / n * 3 + sum(d.podium_rate for d in members) / n * 2)
        ranked = sorted(self.clusters.keys(), key=quality, reverse=True)
        for rank, cid in enumerate(ranked):
            label = self.TIER_LABELS[rank] if rank < len(self.TIER_LABELS) else f"Tier {rank+1}"
            for d in self.clusters[cid]: d.tier_label = label

    def find_similar_drivers(self, target, top_n=5, metric="cosine"):
        scores = []
        for d in self.drivers:
            if d.driver_id == target.driver_id: continue
            score = cosine_similarity(target.feature_vector, d.feature_vector) if metric=="cosine" else -euclidean_distance(target.feature_vector, d.feature_vector)
            scores.append((d, score))
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]

    def get_cluster_summary(self):
        summary = {}
        for cid, members in self.clusters.items():
            if not members: continue
            label = members[0].tier_label
            summary[label] = {
                "driver_count": len(members),
                "avg_win_rate": sum(d.win_rate for d in members)/len(members),
                "top_drivers": [d.full_name for d in sorted(members, key=lambda x: x.wins, reverse=True)[:5]]
            }
        return summary
