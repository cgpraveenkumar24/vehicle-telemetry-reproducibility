# Vehicle Telemetry Reliability: Reproducibility Artifacts

Research code for studying measurement integrity in multi-source vehicle telemetry, with two analysis tracks:

1. **CloudPose:** compare vehicle CAN speed with smartphone GPS speed and evaluate sensitivity to relative temporal shifts.
2. **Illinois IndyToUrbana:** quantify how a controlled coordinate-frame rotation changes an acceleration vector relative to the unrotated reference.

The project is intended to support the research themes in *When the Phone Lies: Engineering Reliable Vehicle Telematics from Commodity Sensors* and related work on evidence-carrying telemetry.

> **Reproducibility status:** This repository provides executable analysis scripts and explicit configuration. Dataset files are not included. Column names and timestamp formats vary by dataset version, so inspect each CSV and pass the relevant column names. Do not treat a successful run as reproducing a paper's published numbers until the dataset version, preprocessing, sign convention, sample counts, and resulting metrics have been reconciled.

## Research questions

- How sensitive is apparent speed disagreement to a relative time shift?
- How does a controlled coordinate-frame perturbation change vector-valued acceleration?
- Can the analysis be rerun with documented parameters and produce machine-readable metrics and figures?

## Validated case-study results

The analysis includes two public-dataset case studies:

- **CloudPose temporal alignment:** across a 341.8-second overlapping trace, MAE decreased from 1.2243 m/s to 0.4731 m/s and RMSE decreased from 1.7950 m/s to 0.6836 m/s after empirical alignment.
- **Illinois coordinate-frame sensitivity:** a 11,804-observation smartphone driving trace is used to investigate coordinate-frame effects on acceleration measurements.

Detailed metrics, interpretation, and limitations are documented in [`docs/validated_results.md`](docs/validated_results.md).

These results are trace-specific and should not be interpreted as universal performance guarantees. Dataset files are not redistributed here.


## Repository layout

```text
.
├── README.md
├── CITATION.cff
├── LICENSE
├── requirements.txt
├── src/
│   ├── cloudpose_alignment.py
│   └── illinois_frame_sensitivity.py
├── tests/
│   └── test_metrics.py
├── docs/
│   ├── methodology.md
│   └── results_provenance.md
└── .github/workflows/tests.yml
```

## Setup

Python 3.10 or later is recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Track A — CloudPose temporal alignment

Obtain the dataset from its official source and place the two CSV files in a local data directory. Do not commit raw data unless its license and terms explicitly permit redistribution.

First inspect headers:

```bash
python -c "import pandas as pd; print(pd.read_csv('data/dataset1_car.csv', nrows=3).columns.tolist())"
python -c "import pandas as pd; print(pd.read_csv('data/dataset1_phone.csv', nrows=3).columns.tolist())"
```

Then run the script, substituting the real column names from the files:

```bash
python src/cloudpose_alignment.py \
  --car data/dataset1_car.csv \
  --phone data/dataset1_phone.csv \
  --car-time TIMESTAMP_COLUMN \
  --car-speed SPEED_MPH_COLUMN \
  --phone-time TIMESTAMP_COLUMN \
  --phone-speed GPS_SPEED_MPS_COLUMN \
  --grid-hz 10 \
  --lag-min -4 --lag-max 4 --lag-step 0.01 \
  --out results/cloudpose
```

The script converts CAN speed from mph to m/s, constructs a common 10-Hz grid over the overlap, interpolates within each stream's observed range, evaluates the unshifted baseline and a lag sweep, and writes:
- `metrics.json`
- `lag_sweep.csv`
- `alignment.png`

The sign of the lag is explicitly reported in the output. Verify the sign convention against your paper before comparing the selected offset with any published value.

## Track B — Illinois coordinate-frame sensitivity

Inspect `IndyToUrbana.csv` and select three acceleration component columns representing one documented coordinate frame:

```bash
python src/illinois_frame_sensitivity.py \
  --input data/IndyToUrbana.csv \
  --ax ACCEL_X_COLUMN --ay ACCEL_Y_COLUMN --az ACCEL_Z_COLUMN \
  --angles 0 30 60 75 90 \
  --out results/illinois
```

The script applies a controlled rotation about the z-axis and calculates the Euclidean difference between each original and rotated vector. It writes `frame_sensitivity.csv` and `frame_sensitivity.png`.

This is a **controlled sensitivity experiment**, not an orientation-estimation algorithm and not evidence that the raw phone axes are already aligned with vehicle axes. Document the source frame, units, gravity handling, and chosen rotation axis for the dataset being analyzed.

## Validation and interpretation

- Report the exact dataset version and checksum where feasible.
- Record sample counts before and after filtering, resampling, and overlap selection.
- Treat the best lag as a trace-specific empirical alignment parameter, not automatically as a hardware clock error or universal sensor latency.
- Avoid claiming general accuracy improvements from a single trace.
- For inferential claims, use a prespecified evaluation protocol and uncertainty estimates that respect temporal dependence.
- Keep generated outputs and raw data out of version control unless there is a clear, licensed reason to include them.

## Known limitations

The scripts require explicit column mapping. Interpolation, timestamp parsing, and rotation assumptions must be checked against the actual dataset documentation. The scripts intentionally do not silently guess units for the smartphone speed or acceleration columns.
