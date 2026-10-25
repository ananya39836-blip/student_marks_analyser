"""
analytics.py - Statistical computation, clustering, correlation, and scoring models
for Student Marks Report Analysis Program.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from typing import Dict, List, Tuple, Any

SUBJECT_COLS = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer_Science", "English"]


def compute_summary_statistics(df: pd.DataFrame, subjects: List[str]) -> pd.DataFrame:
    """Calculate comprehensive statistical benchmarks for all subjects and overall."""
    valid_subjects = [s for s in subjects if s in df.columns]
    stats_data = []

    for s in valid_subjects:
        col = df[s]
        pass_count = (col >= 40).sum()
        fail_count = (col < 40).sum()
        stats_data.append({
            "Subject": s,
            "Mean Score": round(float(col.mean()), 2),
            "Median Score": round(float(col.median()), 2),
            "Std Deviation": round(float(col.std()), 2),
            "Min Score": int(col.min()),
            "Max Score": int(col.max()),
            "25th Percentile": round(float(col.quantile(0.25)), 1),
            "75th Percentile": round(float(col.quantile(0.75)), 1),
            "Pass Rate (%)": round((pass_count / len(df)) * 100, 1),
            "Fail Count": int(fail_count)
        })

    # Overall percentage row
    if "Percentage" in df.columns:
        pct_col = df["Percentage"]
        stats_data.append({
            "Subject": "Overall (%)",
            "Mean Score": round(float(pct_col.mean()), 2),
            "Median Score": round(float(pct_col.median()), 2),
            "Std Deviation": round(float(pct_col.std()), 2),
            "Min Score": round(float(pct_col.min()), 1),
            "Max Score": round(float(pct_col.max()), 1),
            "25th Percentile": round(float(pct_col.quantile(0.25)), 1),
            "75th Percentile": round(float(pct_col.quantile(0.75)), 1),
            "Pass Rate (%)": round(((df["Status"] == "PASSED").sum() / len(df)) * 100, 1),
            "Fail Count": int((df["Status"] == "FAILED").sum())
        })

    return pd.DataFrame(stats_data)


def compute_grade_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate frequencies and percentages of each letter grade."""
    order = ["A+", "A", "B+", "B", "C", "D", "F"]
    counts = df["Grade"].value_counts().reindex(order, fill_value=0)
    percentages = (counts / len(df) * 100).round(1)
    return pd.DataFrame({
        "Grade": counts.index,
        "Student Count": counts.values,
        "Percentage (%)": percentages.values
    })


def identify_toppers(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Identify overall top students based on Total Marks / Percentage."""
    cols = ["Rank", "Roll_No", "Student_Name", "Class", "Section", "Percentage", "Grade", "Attendance_Pct"]
    valid_cols = [c for c in cols if c in df.columns]
    return df.sort_values(by="Total_Marks", ascending=False).head(n)[valid_cols].reset_index(drop=True)


def identify_at_risk_students(df: pd.DataFrame, subjects: List[str]) -> pd.DataFrame:
    """
    Identify students needing immediate academic intervention:
    - Failing in one or more subjects (< 40)
    - Attendance below 75%
    - Overall percentage below 50%
    """
    valid_subjects = [s for s in subjects if s in df.columns]
    at_risk_mask = (df["Percentage"] < 50) | (df["Attendance_Pct"] < 75)
    
    # Check failing any subject
    for s in valid_subjects:
        at_risk_mask |= (df[s] < 40)

    at_risk_df = df[at_risk_mask].copy()
    
    # Generate risk reason
    reasons = []
    for _, row in at_risk_df.iterrows():
        r = []
        if row["Percentage"] < 50:
            r.append(f"Low overall score ({row['Percentage']}%)")
        if row["Attendance_Pct"] < 75:
            r.append(f"Low attendance ({row['Attendance_Pct']}%)")
        failed_subs = [s for s in valid_subjects if row[s] < 40]
        if failed_subs:
            r.append(f"Failed in: {', '.join(failed_subs)}")
        reasons.append("; ".join(r) if r else "Academic Watchlist")
        
    at_risk_df["Risk_Factors"] = reasons
    cols = ["Roll_No", "Student_Name", "Class", "Section", "Percentage", "Attendance_Pct", "Risk_Factors"]
    return at_risk_df[cols].reset_index(drop=True)


def compute_correlation_matrix(df: pd.DataFrame, subjects: List[str]) -> pd.DataFrame:
    """Compute Pearson correlation matrix across subjects and engagement metrics."""
    cols = [s for s in subjects if s in df.columns]
    if "Attendance_Pct" in df.columns:
        cols.append("Attendance_Pct")
    if "Study_Hours_Week" in df.columns:
        cols.append("Study_Hours_Week")
    if "Total_Marks" in df.columns:
        cols.append("Total_Marks")

    return df[cols].corr().round(3)


def perform_kmeans_clustering_3d(df: pd.DataFrame, subjects: List[str], n_clusters: int = 4) -> Tuple[pd.DataFrame, Any, pd.DataFrame]:
    """
    Perform 3D student segmentation using K-Means and dimensionality reduction (PCA)
    to reveal student learning archetypes.
    Returns:
    - df with cluster labels & PCA coordinates (PC1, PC2, PC3)
    - fitted kmeans model
    - cluster profiles summary
    """
    valid_subjects = [s for s in subjects if s in df.columns]
    feature_cols = valid_subjects.copy()
    if "Attendance_Pct" in df.columns:
        feature_cols.append("Attendance_Pct")
    if "Study_Hours_Week" in df.columns:
        feature_cols.append("Study_Hours_Week")

    X = df[feature_cols].copy().fillna(df[feature_cols].mean())

    # PCA down to 3 components for 3D visualization
    pca = PCA(n_components=3, random_state=42)
    coords_3d = pca.fit_transform(X)

    # K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)

    clustered_df = df.copy()
    clustered_df["Cluster"] = clusters
    clustered_df["PC1"] = coords_3d[:, 0]
    clustered_df["PC2"] = coords_3d[:, 1]
    clustered_df["PC3"] = coords_3d[:, 2]

    # Assign meaningful archetype names based on cluster mean percentage
    cluster_means = clustered_df.groupby("Cluster")["Percentage"].mean().to_dict()
    sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1], reverse=True)
    
    archetype_names = {
        sorted_clusters[0][0]: "Top Achievers (Consistent High Mastery)",
        sorted_clusters[1][0]: "Solid Performers (Above Average)",
        sorted_clusters[2][0]: "Moderate / Emerging Potential",
        sorted_clusters[3][0]: "High Risk (Needs Remedial Coaching)"
    }
    
    clustered_df["Archetype"] = clustered_df["Cluster"].map(archetype_names)

    # Summary table
    cluster_summary = clustered_df.groupby("Archetype").agg(
        Student_Count=("Roll_No", "count"),
        Avg_Percentage=("Percentage", "mean"),
        Avg_Attendance=("Attendance_Pct", "mean"),
        Avg_Study_Hours=("Study_Hours_Week", "mean"),
        Pass_Rate=("Status", lambda s: (s == "PASSED").mean() * 100)
    ).round(1).reset_index()

    return clustered_df, kmeans, cluster_summary


def calculate_target_mark_simulation(current_pct: float, current_weight: float = 0.5, target_grade_min_pct: float = 85.0) -> Dict[str, Any]:
    """
    Simulate required marks in upcoming final exam/term to achieve target grade.
    target_pct = (current_pct * current_weight) + (required_pct * (1 - current_weight))
    """
    final_weight = 1.0 - current_weight
    if final_weight <= 0:
        return {"feasible": False, "required_pct": 0, "message": "Current term already represents 100% of final grade."}

    required_pct = (target_grade_min_pct - (current_pct * current_weight)) / final_weight
    feasible = (0 <= required_pct <= 100)
    
    return {
        "feasible": feasible,
        "required_pct": round(required_pct, 1),
        "target_grade_min_pct": target_grade_min_pct,
        "current_pct": current_pct,
        "message": (
            f"You need an average of {required_pct:.1f}% in upcoming assessments to reach the target."
            if feasible else
            (f"Target is mathematically unattainable in this period (requires {required_pct:.1f}%)."
             if required_pct > 100 else "Already achieved target score threshold!")
        )
    }
