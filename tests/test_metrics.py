import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from cloudpose_alignment import metrics
from illinois_frame_sensitivity import rotate_z, summarize

def test_zero_error_metrics():
    x = np.array([0.0, 1.0, 2.0])
    m = metrics(x, x)
    assert m["n"] == 3
    assert m["mae_mps"] == 0.0
    assert m["rmse_mps"] == 0.0

def test_zero_degree_rotation_is_identity():
    x = np.array([[1.0, 2.0, 3.0], [-1.0, 0.0, 0.5]])
    assert np.allclose(rotate_z(x, 0), x)

def test_ninety_degree_rotation_preserves_norm():
    x = np.array([[1.0, 0.0, 2.0]])
    y = rotate_z(x, 90)
    assert np.allclose(np.linalg.norm(x, axis=1), np.linalg.norm(y, axis=1))

def test_zero_degree_sensitivity_is_zero():
    x = np.array([[1.0, 2.0, 3.0], [0.5, -0.2, 0.1]])
    result = summarize(x, 0)
    assert result["mean_vector_error"] < 1e-12
