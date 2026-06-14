**🏎️ F1 DRIVER TIERING AND SIMILARITY ENGINE**

**📌 Overview**

This project is a data-driven engine that analyzes and compares Formula 1 drivers across different eras by transforming career statistics into numerical representations and grouping them into performance-based tiers. Instead of relying on surface-level metrics like total wins or championships, the system captures deeper performance patterns using feature engineering and unsupervised learning.

The end goal:
👉 Automatically generate tier lists (e.g., GOAT, Legendary, Midfield, Backmarker)

👉 Identify statistically similar drivers (“career twins”) across history

**❗ Problem Statement**

Formula 1 has over 70 years of rich data, but comparing drivers fairly is difficult because:

Different eras have different car technologies
Race formats and scoring systems have evolved
Raw stats (wins, titles) ignore context and consistency

*This project addresses that by:*

Converting driver careers into comparable numerical vectors
Using clustering algorithms to group similar drivers
Providing similarity metrics for deeper analysis

🎯 Features

🔢 Driver Vectorization

Each driver is represented as a 9-dimensional feature vector, including:

Win rate
Podium rate
Points per race
Average grid position
DNF rate
Position gain
Qualifying performance
Era encoding (debut year)

All features are normalized to prevent scale bias.

**🧠 Tier List Generation (Clustering)**

Drivers are grouped using a custom implementation of K-Means clustering:

No external ML libraries used
Iterative centroid-based clustering
Handles edge cases like empty clusters
Produces performance tiers such as:

🐐 GOAT
🏆 Legendary
⚖️ Competitive
🔧 Midfield
🚧 Backmarker


🔍 Driver Similarity Engine

*The system compares drivers using:*

Cosine Similarity → similarity in performance patterns
Euclidean Distance → absolute statistical difference

**⚙️ Current Status**

✅ Data ingestion and preprocessing complete
✅ Feature engineering implemented
✅ Object-oriented system fully functional
⏳ Clustering model integration in progress
⏳ Tier generation not finalized yet

**🛠️ Setup and Installation**

1. Clone the repository:

Bash
git clone https://github.com/EzelDilaOzdemir/python-f1-race-and-driver-stats.git
cd python-f1-race-and-driver-stats

2. Install Dependencies:
Ensure you have Python 3.x installed.

4. Data Setup:
Place the raw Kaggle Ergast dataset CSV files directly into the data/ directory before running the scripts.

🚀 How to Run
Execute the main script to run the data pipeline, perform K-Means clustering, and calculate driver similarity:

Bash
python main.py
