# Results Provenance and Reproducibility Record

## 1. Purpose

This document records the provenance, preprocessing assumptions, evaluation parameters, and validation status for the quantitative results reported in the vehicle telemetry reproducibility project.

The project examines two reliability challenges in smartphone-based vehicle telemetry:

1. **Temporal misalignment:** Disagreement between vehicle CAN speed and smartphone GPS speed caused by differences in their observed time series.
2. **Coordinate-frame sensitivity:** Changes in acceleration-vector representation under controlled rotations, illustrating why coordinate-frame handling matters when interpreting smartphone sensor data.

This record distinguishes validated case-study measurements from implementation details that must be confirmed against the exact experimental scripts and source data.

## 2. Case Study A — CloudPose Temporal Alignment

### 2.1 Dataset and scope

| Attribute | Value |
|---|---|
| Dataset | CloudPose |
| Vehicle data file | `dataset1_car.csv` |
| Smartphone data file | `dataset1_phone.csv` |
| Common evaluation frequency | 10 Hz |
| Overlapping evaluation duration | Approximately 341.8 seconds |
| Estimated temporal offset | −2.150 seconds |
| Evaluation objective | Quantify speed disagreement before and after temporal alignment |

The experiment compares vehicle CAN speed with smartphone GPS speed over their overlapping observation interval. The reported results are specific to this evaluated trace.

The raw dataset files are not distributed in this repository. Users must obtain them from their authorized source and verify that their versions match the experimental data used to produce the reported results.

### 2.2 Validated quantitative results

The following measurements have been validated for the evaluated CloudPose trace.

| Metric | Before alignment | After alignment | Relative reduction |
|---|---:|---:|---:|
| Mean absolute error (MAE) | 1.2243 m/s | 0.4731 m/s | 61.4% |
| Root mean squared error (RMSE) | 1.7950 m/s | 0.6836 m/s | 61.9% |
| Median absolute error | 0.7479 m/s | 0.3060 m/s | 59.1% |
| 95th-percentile absolute error | 4.0447 m/s | 1.4613 m/s | 63.9% |
| Steady-state MAE | 0.8124 m/s | 0.3812 m/s | — |
| High-dynamics MAE | 2.1485 m/s | 0.6241 m/s | 70.9% |

Relative reduction is calculated as:

Reduction (%) = ((E_before - E_after) / E_before) × 100

where \(E\) is the corresponding error metric.

The reported temporal offset is approximately −2.150 seconds. Its interpretation depends on the lag sign convention used in the evaluation implementation. The sign convention must be documented alongside any reproduced result.

### 2.3 Interpretation and limitations

Temporal alignment substantially reduced speed disagreement in the evaluated trace, including during high-dynamics segments.

These findings should not be interpreted as proof that:

- All smartphone GPS streams have a fixed latency of 2.150 seconds.
- The estimated offset represents hardware-clock error alone.
- The same improvements will occur across all vehicles, phones, routes, or driving conditions.
- Selecting the best offset on the same trace provides an unbiased estimate of out-of-sample performance.

When the offset is selected by minimizing error on the evaluation trace, the resulting post-alignment error can be optimistic. Generalization claims should therefore be supported by independent traces, a held-out evaluation interval, or a prespecified alignment parameter.

## 3. Case Study B — Illinois Coordinate-Frame Sensitivity

### 3.1 Dataset characteristics

| Attribute | Value |
|---|---|
| Dataset | University of Illinois smartphone driving dataset |
| File | `IndyToUrbana.csv` |
| Approximate route distance | 124 miles |
| Sampling frequency | 2 Hz |
| Observation count | 11,804 |
| Approximate duration | 98.4 minutes |
| Device identified in dataset notes | Samsung Galaxy S6 |
| Maximum observed pitch magnitude | 107.41° |
| Maximum observed roll magnitude | 184.14° |

The case study investigates the sensitivity of smartphone acceleration data to coordinate-frame transformations. Large observed pitch and roll values indicate that the phone's orientation can vary substantially during a driving trace.

### 3.2 Controlled rotation experiment

The implementation applies a controlled rotation to acceleration vectors and evaluates the resulting vector difference. For a rotation matrix \(R\) and acceleration vector \(a\), the implemented sensitivity measure is:

\[
d(a,R)=\|Ra-a\|_2
\]

This experiment demonstrates how a change in coordinate frame can alter the numerical representation of an acceleration vector.

**Interpretation boundary:** A controlled rotation is a sensitivity experiment. It does not, by itself, infer the actual phone-to-vehicle orientation, recover the vehicle coordinate frame, or establish a corrected real-world acceleration signal.

### 3.3 Quantitative reporting requirements

Before reporting numerical Illinois sensitivity findings, record:

- The exact acceleration columns and their units.
- The number of rows retained after parsing and filtering.
- The rotation axis, angle values, and angle convention.
- Whether acceleration includes gravity and whether any gravity compensation is applied.
- Missing-value handling and any filtering or normalization.
- The number of observations evaluated for each rotation.
- The summary statistics and uncertainty estimates used in the report.

Do not infer or substitute sensitivity results that have not been calculated and validated from the experiment.

## 4. Preprocessing and Evaluation Configuration

For every reproduction, record the following settings.

### CloudPose

- Source files and their checksums.
- Timestamp columns, time zones or epoch conventions, and timestamp units.
- Speed columns and units, including any conversion from mph to m/s.
- Duplicate-timestamp handling and sorting rules.
- Overlap-window definition.
- Resampling frequency and interpolation method.
- Lag-search range, resolution, and sign convention.
- Error definitions and the exact sample set used for each metric.
- Definition of steady-state and high-dynamics segments.
- Sample counts before and after preprocessing and alignment.

### Illinois

- Source file and checksum.
- Acceleration columns, units, and coordinate-frame conventions.
- Timestamp and sampling assumptions.
- Missing-value and filtering rules.
- Rotation matrix implementation, axis, and angles.
- Observation counts and aggregation procedure.

If any configuration differs from the experiment that produced the validated measurements, document the difference and avoid presenting the resulting values as an exact reproduction.

## 5. Software and Execution Provenance

Complete this section for each publication-grade reproduction run.

| Field | Value to record |
|---|---|
| Repository URL | `https://github.com/cgpraveenkumar24/vehicle-telemetry-reproducibility` |
| Git commit SHA | Record the exact commit |
| Execution date | Record date and time, including time zone |
| Python version | Record exact version |
| Operating system | Record OS and version |
| Dependency versions | Record installed package versions |
| Dataset source and version | Record source, version, and access date |
| Input file SHA-256 | Record hash for each input file |
| Exact command line | Record the command used to run the experiment |
| Output file SHA-256 | Record hashes for generated outputs, where applicable |
| Publication artifact | Identify the paper figure, table, or result supported |

Example commands, to be adjusted to the actual repository configuration:

```bash
python --version
python -m pip freeze
git rev-parse HEAD
sha256sum dataset1_car.csv dataset1_phone.csv
```

Run file-hashing commands against the actual local input files. Do not publish fabricated hashes or claim that an execution environment has been captured when it has not.

## 6. Validation Status

The reported CloudPose measurements listed in this document are validated case-study results. Their exact reproducibility from the currently published scripts should be claimed only after the source data, configuration, preprocessing, and generated outputs have been reconciled.

For each reproduction, record one of the following statuses:

- **Validated result:** The reported measurement has been independently checked against the underlying experiment.
- **Reproduced:** The published implementation and documented inputs regenerate the reported measurement within the declared tolerance.
- **Partially reproduced:** Some steps or results have been verified, but one or more required inputs or configuration details remain unresolved.
- **Not yet reproduced:** The exact experiment has not been rerun from the published implementation and documented inputs.

A validated result and a fully reproducible software artifact are related but distinct claims.

## 7. Reproducibility Checklist

- [ ] Dataset source, version, and access conditions documented.
- [ ] Input filenames and SHA-256 checksums recorded.
- [ ] Timestamp and unit conversions documented.
- [ ] Preprocessing and filtering rules documented.
- [ ] Resampling and interpolation settings documented.
- [ ] Lag-search parameters and sign convention documented.
- [ ] Illinois rotation parameters and coordinate conventions documented.
- [ ] Sample counts recorded at each processing stage.
- [ ] Python and dependency versions captured.
- [ ] Exact commands and Git commit SHA recorded.
- [ ] Generated outputs and publication figures identified.
- [ ] Independent reproduction status and discrepancies documented.

## 8. Research and Data Availability

The repository provides implementation artifacts and methodological documentation for studying temporal alignment and coordinate-frame sensitivity in multi-source vehicle telemetry.

Raw datasets are not included. Their availability, licensing, and access requirements remain governed by their respective providers.

The findings are case-study results rather than universal performance guarantees. Broader conclusions require additional traces, independent validation, and evaluation under varied devices, vehicles, sampling conditions, and driving dynamics.

## 9. Intended Use

This record is intended to support transparent research review, reproducibility assessment, and verification of the relationship between reported quantitative findings and their experimental implementation.

It should be updated whenever the scripts, dataset versions, preprocessing configuration, or publication results change.
