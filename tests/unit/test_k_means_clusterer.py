"""Unit tests for the K-Means clustering MCP tool."""

import pytest
from app.mcp.k_means_clusterer import cluster_data


def test_kmeans_basic():
    """Test clustering on a simple, clearly separated dataset."""
    # Two distinct clusters in 2D space:
    # Cluster 1: around (0, 0)
    # Cluster 2: around (10, 10)
    data = [
        [0.1, 0.2],
        [0.0, -0.1],
        [-0.2, 0.1],
        [9.9, 10.1],
        [10.0, 9.8],
        [10.2, 10.0],
    ]
    
    # We expect 2 clusters
    result = cluster_data(data, k=2, seed=42)
    
    assert result["converged"] is True
    assert result["iterations"] > 0
    assert len(result["centroids"]) == 2
    assert len(result["labels"]) == len(data)
    
    # Centroids should be close to (0,0) and (10,10)
    c1, c2 = sorted(result["centroids"], key=lambda c: c[0])
    
    # First cluster center should be close to (0, 0)
    assert abs(c1[0]) < 0.5
    assert abs(c1[1]) < 0.5
    
    # Second cluster center should be close to (10, 10)
    assert abs(c2[0] - 10.0) < 0.5
    assert abs(c2[1] - 10.0) < 0.5
    
    # Points 0, 1, 2 should have the same label, and 3, 4, 5 should have the same label
    labels = result["labels"]
    assert labels[0] == labels[1] == labels[2]
    assert labels[3] == labels[4] == labels[5]
    assert labels[0] != labels[3]


def test_kmeans_initialization_methods():
    """Verify that both random and k-means++ initialization methods run and converge."""
    data = [
        [1.0, 1.0], [1.5, 2.0], [3.0, 4.0],
        [5.0, 7.0], [3.5, 5.0], [4.5, 5.0]
    ]
    
    for init_method in ("random", "k-means++"):
        result = cluster_data(data, k=2, init=init_method, seed=42)
        assert result["converged"] is True
        assert len(result["centroids"]) == 2
        assert len(result["labels"]) == len(data)


def test_kmeans_seed_reproducibility():
    """Verify that using the same seed produces identical results."""
    data = [
        [1.0, 2.0], [8.0, 9.0], [1.5, 1.8], [7.8, 8.5],
        [2.0, 1.5], [8.2, 9.1], [1.2, 2.2], [8.5, 8.8]
    ]
    
    res1 = cluster_data(data, k=2, seed=123)
    res2 = cluster_data(data, k=2, seed=123)
    
    assert res1["centroids"] == res2["centroids"]
    assert res1["labels"] == res2["labels"]
    assert res1["inertia"] == res2["inertia"]


def test_kmeans_edge_case_k_equals_1():
    """Test the edge case where k = 1."""
    data = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    result = cluster_data(data, k=1)
    
    assert result["converged"] is True
    assert len(result["centroids"]) == 1
    assert result["labels"] == [0, 0, 0]
    
    # Centroid should be the mean of the data: (3.0, 4.0)
    assert result["centroids"][0] == [3.0, 4.0]


def test_kmeans_edge_case_k_equals_n():
    """Test the edge case where k equals the number of samples."""
    data = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    result = cluster_data(data, k=3, seed=42)
    
    assert len(result["centroids"]) == 3
    # Inertia should be 0 because each point is its own centroid
    assert abs(result["inertia"]) < 1e-9


def test_kmeans_empty_cluster_handling():
    """Test that empty clusters are handled gracefully without division by zero."""
    # We create a dataset with duplicate points, and set k high
    data = [[0.0, 0.0], [0.0, 0.0], [10.0, 10.0]]
    # Since we have duplicate points, if k=3, a naive update might result in an empty cluster
    # if two centroids are placed on the duplicates and one on (10,10), or vice versa.
    # Our implementation handles this by assigning empty clusters to the furthest points.
    result = cluster_data(data, k=3, seed=42)
    assert len(result["centroids"]) == 3
    assert result["converged"] is True


def test_kmeans_validation():
    """Test input validations for parameters."""
    data = [[1.0, 2.0], [3.0, 4.0]]
    
    # Empty data
    with pytest.raises(ValueError, match="cannot be empty"):
        cluster_data([], k=1)
        
    # Non-2D data
    with pytest.raises(ValueError, match="must be a 2D array"):
        cluster_data([1.0, 2.0, 3.0], k=1)
        
    # k <= 0
    with pytest.raises(ValueError, match="greater than 0"):
        cluster_data(data, k=0)
        
    # k > n_samples
    with pytest.raises(ValueError, match="cannot be greater than the number of samples"):
        cluster_data(data, k=3)
        
    # max_iters <= 0
    with pytest.raises(ValueError, match="positive integer"):
        cluster_data(data, k=2, max_iters=0)
        
    # tol < 0
    with pytest.raises(ValueError, match="non-negative"):
        cluster_data(data, k=2, tol=-0.1)
        
    # Invalid init method
    with pytest.raises(ValueError, match="must be 'random' or 'k-means\\+\\+'"):
        cluster_data(data, k=2, init="invalid_init")


def test_fit_and_train():
    """Verify that fit and train functions work correctly and produce equivalent results."""
    from app.mcp.k_means_clusterer import fit, train
    data = [
        [1.0, 2.0], [8.0, 9.0], [1.5, 1.8], [7.8, 8.5],
    ]
    res_fit = fit(data, k=2, seed=42)
    res_train = train(data, k=2, seed=42)
    
    assert res_fit["centroids"] == res_train["centroids"]
    assert res_fit["labels"] == res_train["labels"]
    assert res_fit["inertia"] == res_train["inertia"]


def test_predict():
    """Verify that predict correctly assigns live data to the nearest centroids."""
    from app.mcp.k_means_clusterer import predict
    centroids = [
        [0.0, 0.0],
        [10.0, 10.0]
    ]
    # Point near (0,0) should map to cluster 0
    # Point near (10,10) should map to cluster 1
    live_data = [
        [0.5, -0.5],
        [9.5, 10.2],
        [1.0, 1.0],
    ]
    predictions = predict("A", live_data, centroids)
    assert predictions == [0, 1, 0]


def test_predict_validation():
    """Verify validations in the predict function."""
    from app.mcp.k_means_clusterer import predict
    centroids = [[0.0, 0.0]]
    
    # Empty data
    with pytest.raises(ValueError, match="cannot be empty"):
        predict("A", [], centroids)
        
    # Non-2D data
    with pytest.raises(ValueError, match="must be a 2D array"):
        predict("A", [1.0, 2.0], centroids)
        
    # Empty centroids
    with pytest.raises(ValueError, match="cannot be empty"):
        predict("A", [[1.0, 2.0]], [])
        
    # Non-2D centroids
    with pytest.raises(ValueError, match="must be a 2D array"):
        predict("A", [[1.0, 2.0]], [0.0, 0.0])
        
    # Mismatch dimensions
    with pytest.raises(ValueError, match="dimensions.*must match"):
        predict("A", [[1.0, 2.0, 3.0]], centroids)

