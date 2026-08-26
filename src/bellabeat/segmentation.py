"""User behavioral segmentation.

Segments are derived from the data with k-means clustering rather than
assumed in advance. Cluster count is chosen with silhouette score so the
number of segments is itself evidence-based, not picked to match a
pre-existing narrative.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from . import config

CLUSTER_FEATURES = [
    "avg_daily_steps",
    "avg_sedentary_minutes",
    "avg_active_minutes",
    "avg_daily_calories",
]


def choose_k(features: pd.DataFrame, k_range: range = range(2, 5)) -> tuple[int, dict[int, float]]:
    """Pick the k with the highest silhouette score over the given range.

    Capped at k=4: with only 33 users, finer splits produce segments of
    just 2-3 people each, which is neither statistically robust nor useful
    for a marketing team to act on. len(tier_names) below must stay in
    sync with this upper bound.
    """
    scores: dict[int, float] = {}
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=config.RANDOM_SEED, n_init=10)
        labels = model.fit_predict(features)
        scores[k] = silhouette_score(features, labels)
    best_k = max(scores, key=scores.get)
    return best_k, scores


def segment_users(user_summary: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Cluster users on activity-level features and label clusters by their
    average step count so labels are consistent (Low / Moderate / High) run
    to run even though the underlying cluster index from k-means is
    arbitrary.

    Returns the user_summary table with a `segment` column added, plus a
    report dict describing the chosen k, silhouette scores, and per-segment
    profile means, for documentation purposes.
    """
    complete = user_summary.dropna(subset=CLUSTER_FEATURES).copy()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(complete[CLUSTER_FEATURES])

    best_k, scores = choose_k(scaled)
    model = KMeans(n_clusters=best_k, random_state=config.RANDOM_SEED, n_init=10)
    raw_labels = model.fit_predict(scaled)
    complete["_raw_cluster"] = raw_labels

    cluster_order = (
        complete.groupby("_raw_cluster")["avg_daily_steps"].mean().sort_values().index.tolist()
    )
    # A distinct name set per k, rather than always slicing from one list:
    # slicing a 4-name list down to 2 clusters would mislabel the upper
    # cluster as merely "Moderate" instead of "High".
    tier_name_sets = {
        2: ["Low activity", "High activity"],
        3: ["Low activity", "Moderate activity", "High activity"],
        4: ["Low activity", "Moderate activity", "High activity", "Very high activity"],
    }
    assert len(cluster_order) in tier_name_sets, (
        f"No tier names defined for k={len(cluster_order)}; add an entry to tier_name_sets."
    )
    tier_names = tier_name_sets[len(cluster_order)]
    label_map = dict(zip(cluster_order, tier_names))
    complete["segment"] = complete["_raw_cluster"].map(label_map)

    profile = (
        complete.groupby("segment")[CLUSTER_FEATURES + ["device_usage_days"]]
        .mean()
        .round(1)
    )
    sizes = complete["segment"].value_counts()

    report = {
        "chosen_k": best_k,
        "silhouette_scores": {int(k): round(v, 3) for k, v in scores.items()},
        "segment_sizes": sizes.to_dict(),
        "segment_profile_means": profile.to_dict(orient="index"),
        "users_excluded_missing_features": int(len(user_summary) - len(complete)),
    }

    merged = user_summary.merge(
        complete[["Id", "segment"]], on="Id", how="left"
    )
    return merged, report
