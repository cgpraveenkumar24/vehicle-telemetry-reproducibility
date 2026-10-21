# Validated Results: Multi-Source Vehicle Telemetry

## Overview

This document records the validated results from two public-dataset case studies investigating measurement reliability in smartphone-based vehicle telemetry:

1. **Temporal alignment:** sensitivity of vehicle CAN speed versus smartphone GPS speed to relative time shifts.
2. **Coordinate-frame sensitivity:** effects of smartphone orientation and coordinate-frame changes on acceleration measurements.

The experiments motivate a stream-first telemetry architecture in which time alignment, coordinate-frame interpretation, and measurement quality are evaluated before downstream event detection or decision-making.

## Case Study 1: CloudPose Temporal Alignment

### Dataset and evaluation

The CloudPose case study uses `dataset1_car.csv` and `dataset1_phone.csv`, containing vehicle CAN and smartphone telemetry, respectively.

The streams were evaluated over their overlapping 341.8-second interval on a common 10 Hz grid. The phone and vehicle streams were compared before and after empirical temporal alignment.

The selected relative shift was approximately **−2.150 seconds**, under the sign convention used in the analysis.

### Results

| Metric | Before alignment | After alignment |
|---|---:|---:|
| Mean absolute error (MAE) | 1.2243 m/s | 0.4731 m/s |
| Root mean square error (RMSE) | 1.7950 m/s | 0.6836 m/s |
| Median absolute error | 0.7479 m/s | 0.3060 m/s |
| 95th-percentile absolute error | 4.0447 m/s | 1.4613 m/s |

### Error reduction

| Metric | Relative reduction |
|---|---:|
| MAE | 61.4% |
| RMSE | 61.9% |
| Median absolute error | 59.1% |
| 95th-percentile absolute error | 63.9% |

The results show that temporal alignment materially reduced the observed disagreement between the two speed streams in this trace. The improvement was visible in both typical error and the upper tail of the error distribution.

### Driving-dynamics analysis

The trace was also evaluated across steady-state and high-dynamics segments.

| Segment | MAE before alignment | MAE after alignment |
|---|---:|---:|
| Steady state | 0.8124 m/s | 0.3812 m/s |
| High dynamics | 2.1485 m/s | 0.6241 m/s |

For the high-dynamics segment, MAE decreased by approximately **70.9%**. This suggests that temporal alignment can be especially consequential when vehicle speed changes rapidly.

### Interpretation

A discrepancy between smartphone-derived and vehicle-derived speed should not automatically be attributed to sensor inaccuracy. Relative timing can be a significant contributing factor.

The observed lag is specific to the evaluated trace and processing configuration. It should not be interpreted as a universal smartphone latency or hardware clock error. Because the best lag was selected using the evaluated trace, independent or held-out evaluation is appropriate before making broader predictive or generalization claims.

## Case Study 2: Illinois Smartphone Driving Trace

### Dataset characteristics

The Illinois case study uses `IndyToUrbana.csv`, a smartphone driving trace collected using a Samsung Galaxy S6.

| Characteristic | Recorded value |
|---|---:|
| Approximate route distance | 124 miles |
| Sampling frequency | 2 Hz |
| Number of observations | 11,804 |
| Approximate duration | 98.4 minutes |
| Maximum observed pitch magnitude | 107.41° |
| Maximum observed roll magnitude | 184.14° |

The recorded orientation variation motivates careful treatment of coordinate frames when interpreting phone-derived acceleration and other vector-valued measurements.

### Analysis objective

The coordinate-frame sensitivity experiment applies a controlled rotation to acceleration vectors and compares the transformed vectors with their original representations. This isolates the mathematical effect of a specified coordinate transformation.

The analysis is intended to demonstrate why coordinate-frame assumptions must be documented and validated before acceleration measurements are used for driving-event detection or other downstream decisions.

A controlled rotation is not, by itself, an estimate of the phone's actual orientation relative to the vehicle. The transformation axis, acceleration convention, gravity handling, and preprocessing must be interpreted in the context of the dataset.

## Architectural Implications

Together, the case studies illustrate two distinct sources of measurement uncertainty:

- **Temporal uncertainty:** streams representing the same physical process may disagree when their timestamps are not appropriately aligned.
- **Coordinate-frame uncertainty:** vector measurements may be misinterpreted when the sensor coordinate frame and the intended vehicle frame are not reconciled.

These findings motivate a telemetry processing pipeline that explicitly evaluates measurement time, coordinate frame, source provenance, and quality before normalizing streams and triggering downstream events.

A conceptual processing sequence is:

`RAW STREAMS → TIME / FRAME / PROVENANCE → QUALITY GATE → NORMALIZED STREAM → EVENT DETECTION → DECISION / EVIDENCE`

## Reproducibility

The repository provides scripts for the temporal-alignment and coordinate-frame sensitivity analyses, along with methodology documentation and tests.

To reproduce the reported results:

1. Obtain the corresponding public datasets from their authoritative sources.
2. Verify dataset versions, licensing terms, file integrity, and input units.
3. Apply the documented column mappings and preprocessing.
4. Execute the scripts using the reported sampling, lag-search, and transformation parameters.
5. Compare generated outputs against the recorded results and preserve the run configuration.

Raw datasets are not included in this repository. Consult the methodology and results-provenance documents for assumptions and the information required to record a reproducible run.

## Scope and Limitations

The numerical results reported here apply to the evaluated traces and configurations. They do not establish universal error reductions across all vehicles, smartphones, driving conditions, or sensor combinations.

Temporal alignment and coordinate-frame reconciliation address different problems and should be evaluated independently. Further validation across multiple traces, held-out intervals, and operating conditions is necessary to establish generalizability.

## Research Significance

The case studies provide empirical support for treating time alignment and coordinate-frame interpretation as explicit stages of vehicle telemetry quality assurance rather than implicit assumptions. This is particularly relevant to telemetry systems where sensor-derived measurements feed safety-related event detection, fleet analytics, or evidence-producing cyber-physical applications.
