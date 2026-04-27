🏎️ F1 Driver Tiering & Similarity Engine
📌 Overview

This project is a data-driven engine that analyzes and compares Formula 1 drivers across different eras by transforming career statistics into numerical representations and grouping them into performance-based tiers.

Instead of relying on surface-level metrics like total wins or championships, the system captures deeper performance patterns using feature engineering and unsupervised learning.

The end goal:
👉 Automatically generate tier lists (e.g., GOAT, Legendary, Midfield, Backmarker)
👉 Identify statistically similar drivers (“career twins”) across history

❗ Problem Statement

Formula 1 has over 70 years of rich data, but comparing drivers fairly is difficult because:

Different eras have different car technologies
Race formats and scoring systems have evolved
Raw stats (wins, titles) ignore context and consistency

This project addresses that by:

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

🧠 Tier List Generation (Clustering)

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

The system compares drivers using:

Cosine Similarity → similarity in performance patterns
Euclidean Distance → absolute statistical difference

This allows:

Cross-era comparisons
Finding “career twins”
More nuanced analysis than rankings alone
🏗️ System Architecture

The project follows a structured data pipeline:

Data Ingestion
Loads 10 CSV files from the Ergast dataset
Uses Python’s built-in csv module (no Pandas)
Preprocessing
Handles missing/null values safely
Cleans and links relational data
Feature Engineering
Converts raw stats → normalized vectors
Modeling
Custom K-Means clustering implementation
Query Layer
Driver comparison & tier output
🧱 Core Classes
Driver
Stores all career data
Computes performance metrics
Generates normalized feature vector
Team
Aggregates driver data
Computes team-level performance vectors
DataLoader
Handles CSV ingestion
Manages relationships between datasets
Ensures correct loading order
ClusterManager
Implements K-Means from scratch
Assigns drivers to clusters
Updates centroids iteratively
⚙️ Current Status

✅ Data ingestion and preprocessing complete
✅ Feature engineering implemented
✅ Object-oriented system fully functional
⏳ Clustering model integration in progress
⏳ Tier generation not finalized yet
