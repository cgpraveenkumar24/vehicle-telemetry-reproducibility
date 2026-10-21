#!/usr/bin/env python3
"""Evaluate relative temporal-shift sensitivity between CAN and phone speed."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MPH_TO_MPS = 0.44704

def parse_time(series: pd.Series) -> pd.Series:
    """Parse numeric epoch/relative seconds or common datetime strings to seconds."""
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() > 0.95:
        values = numeric.to_numpy(dtype=float)
        # Large values are likely epoch milliseconds or nanoseconds; require user review.
        med = np.nanmedian(np.abs(values))
        if med > 1e16:
            values = values / 1e9
        elif med > 1e12:
            values = values / 1e3
        return pd.Series(values, index=series.index)
    parsed = pd.to_datetime(series, errors="coerce", utc=True)
    if parsed.notna().mean() < 0.95:
        raise ValueError("Could not parse timestamp column. Normalize it to seconds or ISO timestamps.")
    return pd.Series(parsed.astype("int64").to_numpy(dtype=float) / 1e9, index=series.index)

def metrics(reference: np.ndarray, candidate: np.ndarray) -> dict:
    err = np.abs(reference - candidate)
    return {
        "n": int(err.size),
        "mae_mps": float(np.mean(err)),
        "rmse_mps": float(np.sqrt(np.mean((reference - candidate) ** 2))),
        "median_absolute_error_mps": float(np.median(err)),
        "p95_absolute_error_mps": float(np.percentile(err, 95)),
        "mae_mph": float(np.mean(err) / MPH_TO_MPS),
        "rmse_mph": float(np.sqrt(np.mean((reference - candidate) ** 2)) / MPH_TO_MPS),
    }

def prepare(path: str, time_col: str, speed_col: str, speed_scale: float) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in (time_col, speed_col):
        if col not in df.columns:
            raise ValueError(f"Column {col!r} not found in {path}. Available columns: {list(df.columns)}")
    out = pd.DataFrame({
        "t": parse_time(df[time_col]),
        "v": pd.to_numeric(df[speed_col], errors="coerce") * speed_scale,
    }).replace([np.inf, -np.inf], np.nan).dropna()
    out = out.sort_values("t").drop_duplicates("t", keep="first")
    if len(out) < 3:
        raise ValueError(f"Not enough valid rows in {path} after parsing.")
    return out

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--car", required=True)
    p.add_argument("--phone", required=True)
    p.add_argument("--car-time", required=True)
    p.add_argument("--car-speed", required=True, help="Vehicle CAN speed column; assumed mph")
    p.add_argument("--phone-time", required=True)
    p.add_argument("--phone-speed", required=True, help="Phone GPS speed column; assumed m/s")
    p.add_argument("--grid-hz", type=float, default=10.0)
    p.add_argument("--lag-min", type=float, default=-4.0)
    p.add_argument("--lag-max", type=float, default=4.0)
    p.add_argument("--lag-step", type=float, default=0.01)
    p.add_argument("--out", default="results/cloudpose")
    args = p.parse_args()
    if args.grid_hz <= 0 or args.lag_step <= 0 or args.lag_max < args.lag_min:
        p.error("grid-hz and lag-step must be positive; lag-max must be >= lag-min")
    car = prepare(args.car, args.car_time, args.car_speed, MPH_TO_MPS)
    phone = prepare(args.phone, args.phone_time, args.phone_speed, 1.0)
    # Put both timestamps on a relative timeline. The common origin has no effect on lag differences.
    origin = max(car.t.min(), phone.t.min())
    car["t"] -= origin
    phone["t"] -= origin
    dt = 1.0 / args.grid_hz
    start, end = max(car.t.min(), phone.t.min()), min(car.t.max(), phone.t.max())
    if end <= start:
        raise ValueError("No overlapping time interval between the two streams.")
    grid = np.arange(start, end + dt * 0.25, dt)
    cv = np.interp(grid, car.t.to_numpy(), car.v.to_numpy())
    pv = np.interp(grid, phone.t.to_numpy(), phone.v.to_numpy())
    # Lag convention: candidate phone value at t + lag is compared with CAN at t.
    lags = np.round(np.arange(args.lag_min, args.lag_max + args.lag_step * 0.5, args.lag_step), 10)
    rows = []
    for lag in lags:
        shifted = np.interp(grid + lag, grid, pv, left=np.nan, right=np.nan)
        valid = np.isfinite(cv) & np.isfinite(shifted)
        if valid.sum() < 3:
            continue
        m = metrics(cv[valid], shifted[valid])
        rows.append({"lag_seconds": float(lag), **m})
    sweep = pd.DataFrame(rows)
    if sweep.empty:
        raise ValueError("Lag sweep produced no valid overlapping pairs.")
    baseline_lag = sweep.iloc[(sweep.lag_seconds.abs()).argmin()]
    best = sweep.loc[sweep.rmse_mps.idxmin()]
    best_phone = np.interp(grid + float(best.lag_seconds), grid, pv, left=np.nan, right=np.nan)
    valid = np.isfinite(best_phone)
    result = {
        "analysis": "cloudpose_relative_temporal_alignment",
        "inputs": {"car_csv": args.car, "phone_csv": args.phone,
                   "car_time_column": args.car_time, "car_speed_column": args.car_speed,
                   "phone_time_column": args.phone_time, "phone_speed_column": args.phone_speed},
        "assumptions": {"car_speed_unit": "mph", "phone_speed_unit": "m/s",
                        "grid_hz": args.grid_hz,
                        "lag_convention": "phone(t + lag) compared with CAN(t)",
                        "lag_selection_metric": "minimum RMSE on the same trace; descriptive sensitivity analysis"},
        "overlap": {"start_relative_seconds": float(start), "end_relative_seconds": float(end),
                    "grid_points": int(len(grid))},
        "baseline": metrics(cv[valid], np.interp(grid[valid], grid, pv)),
        "best_lag_seconds": float(best.lag_seconds),
        "best_lag_metrics": {k: (int(best[k]) if k == "n" else float(best[k]))
                             for k in ("n", "mae_mps", "rmse_mps", "median_absolute_error_mps",
                                       "p95_absolute_error_mps", "mae_mph", "rmse_mph")},
        "warning": "The selected lag is trace-specific and is not automatically a hardware-clock offset or universal latency."
    }
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sweep.to_csv(out / "lag_sweep.csv", index=False)
    (out / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(sweep.lag_seconds, sweep.rmse_mps, label="RMSE (m/s)")
    ax.axvline(float(best.lag_seconds), linestyle="--", label=f"minimum RMSE: {best.lag_seconds:.2f} s")
    ax.set(xlabel="Relative phone lag (s)", ylabel="RMSE (m/s)", title="CloudPose temporal-shift sensitivity")
    ax.grid(True, alpha=0.3); ax.legend(); fig.tight_layout()
    fig.savefig(out / "alignment.png", dpi=180); plt.close(fig)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
