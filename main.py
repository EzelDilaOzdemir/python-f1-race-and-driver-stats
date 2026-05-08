def main():
 
    # 1. Load all CSV data
    loader = DataLoader(data_dir="./f1_data/")
    loader.load_all()
 
    all_drivers = list(loader.drivers.values())
 
    # 2. Run K-Means clustering
    cm = ClusterManager(k=5, max_iterations=300, random_seed=42)
    cm.fit(all_drivers)
 
    # 3. Print tier summary
    print("=" * 60)
    print("TIER SUMMARY")
    print("=" * 60)
    for tier, info in cm.get_cluster_summary().items():
        print(f"\n  {tier}")
        print(f"    Drivers in tier  : {info['driver_count']}")
        print(f"    Avg win rate     : {info['avg_win_rate']:.1%}")
        print(f"    Avg podium rate  : {info['avg_podium_rate']:.1%}")
        print(f"    Top by wins      : {', '.join(info['top_drivers'])}")
 
    # 4. Similarity queries
    print("\n" + "=" * 60)
    print("SIMILARITY QUERIES")
    print("=" * 60)
 
    surname_idx = {d.surname.lower(): d for d in all_drivers}
 
    queries = [
        ("hamilton",   "cosine",     "cross-era"),
        ("schumacher", "euclidean",  "same-scale"),
        ("verstappen", "cosine",     "modern-era"),
    ]
 
    for surname, metric, note in queries:
        target = surname_idx.get(surname)
        if target is None or not target.feature_vector:
            print(f"\n  '{surname}' not found.")
            continue
 
        print(f"\n  Most similar to {target.full_name}  "
              f"[{metric} | {note}]")
        for rank, (drv, score) in enumerate(
            cm.find_similar_drivers(target, top_n=5, metric=metric), 1
        ):
            score_str = (f"cosine={score:+.4f}"
                         if metric == "cosine"
                         else f"dist={-score:.4f}")
            print(f"    {rank}. {drv.full_name:<25} {score_str}"
                  f"  tier={drv.tier_label}  wins={drv.wins}")
 
    # 5. Individual driver cards
    print("\n" + "=" * 60)
    print("DRIVER CARDS")
    print("=" * 60)
    for surname in ["hamilton", "schumacher", "senna", "fangio", "verstappen"]:
        d = surname_idx.get(surname)
        if d is None:
            continue
        total_pts = d.race_points + d.sprint_points
        print(
            f"\n  {d.full_name} ({d.nationality}, debut {d.debut_year})"
            f"\n    Tier          : {d.tier_label}"
            f"\n    Races         : {d.races_started}"
            f"\n    Wins          : {d.wins}  ({d.win_rate:.1%})"
            f"\n    Podiums       : {d.podiums}  ({d.podium_rate:.1%})"
            f"\n    Points        : {total_pts:.1f}"
            f"\n    Championships : {d.championships}"
            f"\n    DNF rate      : {d.dnf_rate:.1%}"
            f"\n    Avg grid pos  : {d.avg_grid:.1f}"
            f"\n    Avg quali pos : {d.avg_quali:.1f}"
        )
 
 
if __name__ == "__main__":
    main()
 
