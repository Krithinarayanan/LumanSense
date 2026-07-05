"""Pedestrian density clustering service.

This module provides a functional implementation of the K-Means clustering
algorithm to categorize pedestrian density zones. It supports clustering of
footfall telemetry and zone-wise classification of traffic patterns.
"""

import logging
from typing import Any

import numpy as np
from mcp.server.fastmcp import FastMCP

from app.mcp.database_mcp import save_cluster_training_history

logger = logging.getLogger("luman_sense")

mcp = FastMCP("KMeansClustererMCP")


def cluster_data(
    data: Any,
    k: int,
    init: str = "random",
    max_iters: int = 100,
    tol: float = 1e-4,
    seed: int | None = None,
) -> dict:
    """Cluster data using the K-Means algorithm.

    Args:
        data: A 2D array or list of lists containing the dataset.
        k: The number of clusters.
        init: The initialization method ('random' or 'k-means++').
        max_iters: The maximum number of iterations.
        tol: The convergence tolerance.
        seed: Random seed for reproducibility.

    Returns:
        A dictionary with clustering results.
    """
    # validations
    if not isinstance(data, np.ndarray):
        if data is None or (isinstance(data, list | tuple) and len(data) == 0):
            raise ValueError("Data cannot be empty")
        try:
            data_arr = np.array(data, dtype=float)
        except Exception as e:
            raise ValueError("Data must be a 2D array") from e
    else:
        data_arr = data.astype(float)

    if data_arr.size == 0 or len(data_arr) == 0:
        raise ValueError("Data cannot be empty")

    if data_arr.ndim != 2:
        raise ValueError("Data must be a 2D array")

    if not isinstance(k, int) or k <= 0:
        raise ValueError("k must be greater than 0")

    if k > len(data_arr):
        raise ValueError("k cannot be greater than the number of samples")

    if not isinstance(max_iters, int) or max_iters <= 0:
        raise ValueError("max_iters must be a positive integer")

    if not isinstance(tol, float | int) or tol < 0:
        raise ValueError("tol must be non-negative")

    if init not in ("random", "k-means++"):
        raise ValueError("init must be 'random' or 'k-means++'")

    if seed is not None:
        np.random.seed(seed)

    # Initialization
    n_samples, _n_features = data_arr.shape
    if init == "random":
        indices = np.random.choice(n_samples, size=k, replace=False)
        centroids = data_arr[indices].copy()
    else:  # k-means++
        centroids = []
        first_idx = np.random.choice(n_samples)
        centroids.append(data_arr[first_idx])
        for _ in range(1, k):
            distances = np.array(
                [min(np.sum((x - c) ** 2) for c in centroids) for x in data_arr]
            )
            if np.sum(distances) == 0:
                probs = np.ones(n_samples) / n_samples
            else:
                probs = distances / np.sum(distances)
            next_idx = np.random.choice(n_samples, p=probs)
            centroids.append(data_arr[next_idx])
        centroids = np.array(centroids)

    converged = False
    iterations = 0
    labels = np.zeros(n_samples, dtype=int)

    for iteration in range(1, max_iters + 1):
        iterations = iteration
        # 1. Assignment
        new_labels = np.zeros(n_samples, dtype=int)
        for i, x in enumerate(data_arr):
            new_labels[i] = np.argmin([np.sum((x - c) ** 2) for c in centroids])

        labels = new_labels

        # 2. Update centroids
        new_centroids = np.zeros_like(centroids)
        for j in range(k):
            mask = labels == j
            if np.any(mask):
                new_centroids[j] = data_arr[mask].mean(axis=0)
            else:
                # Handle empty cluster: reinitialize with the furthest point
                dists = np.array(
                    [
                        np.sum((data_arr[idx] - centroids[labels[idx]]) ** 2)
                        for idx in range(n_samples)
                    ]
                )
                furthest_idx = np.argmax(dists)
                new_centroids[j] = data_arr[furthest_idx]
                labels[furthest_idx] = j

        # 3. Check convergence
        shift = np.sqrt(np.sum((new_centroids - centroids) ** 2, axis=1))
        if np.all(shift < tol):
            converged = True
            centroids = new_centroids
            break

        centroids = new_centroids

    # Calculate inertia
    inertia = 0.0
    for i, x in enumerate(data_arr):
        inertia += np.sum((x - centroids[labels[i]]) ** 2)

    return {
        "converged": converged,
        "iterations": iterations,
        "centroids": centroids.tolist(),
        "labels": labels.tolist(),
        "inertia": float(inertia),
    }


@mcp.tool()
def predict(zone, data: Any, centroids: Any) -> list[int]:
    """Classifies live pedestrian flow data into the closest traffic density categories.

    Args:
        data: Pedestrian flow readings to classify.
        centroids: Discovered traffic density cluster centers.

    Returns:
        A list of assigned traffic density cluster indices.
    """
    # validation
    if not isinstance(data, np.ndarray):
        if data is None or (isinstance(data, list | tuple) and len(data) == 0):
            raise ValueError("Data cannot be empty")
        try:
            data_arr = np.array(data, dtype=float)
        except Exception as e:
            raise ValueError("Data must be a 2D array") from e
    else:
        data_arr = data.astype(float)

    if data_arr.size == 0 or len(data_arr) == 0:
        raise ValueError("Data cannot be empty")

    if data_arr.ndim != 2:
        raise ValueError("Data must be a 2D array")

    if not isinstance(centroids, np.ndarray):
        if centroids is None or (
            isinstance(centroids, list | tuple) and len(centroids) == 0
        ):
            raise ValueError("Centroids cannot be empty")
        try:
            centroids_arr = np.array(centroids, dtype=float)
        except Exception as e:
            raise ValueError("Centroids must be a 2D array") from e
    else:
        centroids_arr = centroids.astype(float)

    if centroids_arr.size == 0 or len(centroids_arr) == 0:
        raise ValueError("Centroids cannot be empty")

    if centroids_arr.ndim != 2:
        raise ValueError("Centroids must be a 2D array")

    if data_arr.shape[1] != centroids_arr.shape[1]:
        raise ValueError("Feature dimensions of data and centroids must match")

    # predict
    labels = []

    for x in data_arr:
        dists = [np.sqrt(np.sum((x - c) ** 2)) for c in centroids_arr]
        labels.append(int(np.argmin(dists)))

    logger.info("zone: %s", zone)
    logger.info("pedestrian count input: %s", data_arr)
    logger.info("centroid values: %s", centroids_arr)
    logger.info("predicted state: %s", labels)
    return labels


@mcp.tool()
def get_traffic_clusters() -> Any:
    """Processes historical pedestrian flow logs to build zone-wise traffic density clusters.

    Returns:
        A tuple of (cluster_discovery_map, centroids) representing classified pedestrian flow records and zone-wise density centroids.
    """
    from collections import defaultdict

    from app.data_parser import parse_traffic_data

    # Group counts by zone and scale to align with real-time counts
    ZONE_SCALING_FACTORS = {
        "A": 7.75,
        "B": 5.0,
        "C": 2.0,
        "D": 10.33,
    }

    records = parse_traffic_data()

    # Group by (timestamp, zone) and average the vehicles
    grouped = defaultdict(list)
    for r in records:
        grouped[(r["timestamp"], r["zone"])].append(r["vehicles"])

    counts = {}
    for (ts, zone), vals in grouped.items():
        avg_vehicles = sum(vals) / len(vals)
        scale = ZONE_SCALING_FACTORS.get(zone, 1.0)
        counts[(ts, zone)] = avg_vehicles / scale

    zone_data = defaultdict(list)
    for (ts, zone), count in counts.items():
        scale = ZONE_SCALING_FACTORS.get(zone, 1.0)
        zone_data[zone].append(
            {"timestamp": ts, "zone": zone, "pedestrians": float(count) * scale}
        )

    # 2. Calculate the EMA with respect to timestamp on pedestrians count per zone.
    alpha = 0.3
    for zone in zone_data:
        # Sort by timestamp chronologically
        zone_data[zone].sort(key=lambda x: x["timestamp"])
        current_ema = None
        for item in zone_data[zone]:
            ped = item["pedestrians"]
            if current_ema is None:
                current_ema = ped
            else:
                current_ema = alpha * ped + (1 - alpha) * current_ema
            item["ema"] = current_ema

    # 3. Cluster per zone
    cluster_discovery_map = {}
    centroids = {}
    cluster_map = {
        0: "LOW_TRAFFIC",
        1: "CLEARING_TRAFFIC",
        2: "MODERATE_TRAFFIC",
        3: "TRAFFIC_SURGE",
        4: "PEAK_TRAFFIC",
    }

    for zone in sorted(zone_data.keys()):
        zone_points = zone_data[zone]
        points = [[item["pedestrians"], item["ema"]] for item in zone_points]

        # Determine number of clusters k
        k_zone = min(5, len(points))
        if k_zone == 0:
            cluster_discovery_map[zone] = []
            centroids[zone] = []
            continue

        res = cluster_data(points, k=k_zone, seed=42)

        centroids_list = res["centroids"]
        # Sort centroids by sum of elements (density metric: pedestrians + ema)
        sorted_indices = sorted(
            range(len(centroids_list)), key=lambda idx: sum(centroids_list[idx])
        )

        # Create a mapping from old arbitrary cluster ID to new sorted cluster ID
        old_to_new_id = {
            old_idx: new_idx for new_idx, old_idx in enumerate(sorted_indices)
        }

        # Reorder the centroids to match the new sorted order (0, 1, ..., k-1)
        sorted_centroids = [centroids_list[idx] for idx in sorted_indices]
        centroids[zone] = sorted_centroids

        # Map labels in points to their new sorted cluster IDs
        labels = [old_to_new_id[lbl] for lbl in res["labels"]]
        for idx, item in enumerate(zone_points):
            item["cluster_id"] = labels[idx]
            item["cluster_label"] = cluster_map[labels[idx]]

        cluster_discovery_map[zone] = zone_points

    # iterate centroids and pretty print - zone, pedestrians, ema, cluster_id, cluster_label, timestamp
    for zone in sorted(cluster_discovery_map.keys()):
        logger.info("\n" + "=" * 80)
        logger.info("Cluster Centers for Zone %s", zone)
        logger.info("=" * 80)

        zone_points = cluster_discovery_map[zone]
        for item in zone_points:
            save_cluster_training_history(item)

    return cluster_discovery_map, centroids


def main():
    mcp.run()


if __name__ == "__main__":
    main()
