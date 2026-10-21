#!/usr/bin/env python3
"""Quantify vector error caused by controlled rotation of acceleration coordinates."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def rotate_z(vectors: np.ndarray, angle_deg: float) -> np.ndarray:
    """Rotate Nx3 vectors about the z-axis by angle_deg."""
    theta = np.deg2rad(angle_deg)
    c, s = np.cos(theta), np.sin(theta)
    r = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    return vectors @ r.T

def summarize(vectors: np.ndarray, angle_deg: float) -> dict:
    rotated = rotate_z(vectors, angle_deg)
    error = np.linalg.norm(rotated - vectors, axis=1)
    return {
        "rotation_deg": float(angle_deg),
        "n": int(len(error)),
        "mean_vector_error": float(np.mean(error)),
        "median_vector_error": float(np.median(error)),
        "p95_vector_error": float(np.percentile(error, 95)),
        "max_vector_error": float(np.max(error)),
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--ax", required=True, help="Acceleration x component column")
    p.add_argument("--ay", required=True, help="Acceleration y component column")
    p.add_argument("--az", required=True, help="Acceleration z component column")
    p.add_argument("--angles", nargs="+", type=float, default=[0, 30, 60, 75, 90])
    p.add_argument("--out", default="results/illinois")
    args = p.parse_args()
    df = pd.read_csv(args.input)
    cols = [args.ax, args.ay, args.az]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns {missing}. Available columns: {list(df.columns)}")
    vectors = df[cols].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    vectors = vectors[np.isfinite(vectors).all(axis=1)]
    if len(vectors) < 3:
        raise ValueError("Not enough complete numeric acceleration vectors.")
    rows = [summarize(vectors, a) for a in args.angles]
    result = pd.DataFrame(rows).sort_values("rotation_deg")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "frame_sensitivity.csv", index=False)
    metadata = {
        "analysis": "controlled_coordinate_frame_rotation_sensitivity",
        "input_csv": args.input,
        "acceleration_columns": cols,
        "valid_vector_count": int(len(vectors)),
        "rotation_model": "rigid rotation about z-axis; compare each rotated vector to its unrotated vector",
        "interpretation": "Controlled sensitivity analysis only; this is not an orientation estimator or proof of true vehicle-frame alignment."
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(result.rotation_deg, result.mean_vector_error, marker="o", label="Mean vector error")
    ax.plot(result.rotation_deg, result.p95_vector_error, marker="s", label="95th percentile")
    ax.set(xlabel="Controlled rotation (degrees)", ylabel="Vector error (input acceleration units)",
           title="Illinois coordinate-frame sensitivity")
    ax.grid(True, alpha=0.3); ax.legend(); fig.tight_layout()
    fig.savefig(out / "frame_sensitivity.png", dpi=180); plt.close(fig)
    print(result.to_string(index=False))

if __name__ == "__main__":
    main()
