# Methodology and assumptions

## CloudPose

The vehicle CAN speed is assumed to be in miles per hour and is converted using 1 mph = 0.44704 m/s. Phone GPS speed is assumed to be in m/s. Both streams are sorted by parsed time and duplicate timestamps are removed. A shared grid is constructed over the time overlap and linear interpolation is used to compare the streams.

For candidate lag `l`, the script compares CAN speed at time `t` with interpolated phone speed at `t + l`. Candidate shifts that extend beyond the observed phone range are excluded rather than extrapolated. The primary selected shift minimizes RMSE over the remaining pairs. Since selection and evaluation use the same trace, the selected minimum is descriptive and may be optimistic. Use a prespecified lag or held-out interval for confirmatory evaluation.

The code accepts numeric seconds, epoch milliseconds, epoch nanoseconds, or parseable datetime values. Verify timestamp units and epoch assumptions before interpreting a lag in seconds.

## Illinois coordinate-frame sensitivity

For each selected acceleration vector `a`, the script applies a rotation matrix about the z-axis and calculates `||R a - a||_2`. This measures how much the vector representation changes under the specified controlled rotation. It does not infer the phone's orientation relative to the vehicle, estimate a transformation from orientation sensors, or establish the true vehicle-frame acceleration.

Before making publication claims, document:
- whether acceleration includes gravity;
- the units and coordinate convention of each component;
- the axis used for the perturbation and why;
- treatment of missing values and any filtering;
- the exact row count after preprocessing.

## Statistical reporting

For time-series data, rows are not generally independent. Confidence intervals and hypothesis tests should preserve temporal structure (for example, block bootstrap) and should be planned before looking at the final outcome. Report effect sizes and uncertainty, not only point estimates.
