from DataLoader import DataLoader
from cluster import ClusterManager

def main():
    # 1. Load data
    loader = DataLoader(data_dir="./f1_data/")
    loader.load_all()
    all_drivers = list(loader.drivers.values())

    # 2. Run K-Means
    cm = ClusterManager(k=5)
    cm.fit(all_drivers)

    # 3. Output results
    print("\n" + "="*20 + " TIER SUMMARY " + "="*20)
    for tier, info in cm.get_cluster_summary().items():
        print(f"{tier}: {info['driver_count']} drivers. Top: {', '.join(info['top_drivers'])}")

    print("\n" + "="*20 + " SIMILARITY " + "="*20)
    
    def find_driver(drivers, surname):
        matches = [d for d in drivers if d.surname.lower() == surname.lower()]
        return max(matches, key=lambda d: d.races_started) if matches else None

    for name in ["hamilton", "verstappen", "schumacher", "senna"]:
        target = find_driver(all_drivers, name)
        if target:
            print(f"\nSimilar to {target.full_name}:")
            for drv, score in cm.find_similar_drivers(target):
                print(f"  - {drv.full_name} ({drv.tier_label})")



if __name__ == "__main__":
    main()

