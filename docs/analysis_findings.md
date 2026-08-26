# Analysis Findings

**Phase covered:** Analyze
**Reproduces from:** `scripts/run_pipeline.py`, `outputs/tables/*.csv`, `outputs/tables/statistical_test_results.json`, `outputs/tables/segmentation_report.json`
**Sample:** 33 users, 31 days (2016-04-12 to 2016-05-12); see `docs/data_quality_report.md` for full caveats before treating any number here as generalizable.

All figures referenced below are in `outputs/figures/`.

---

## 1. How active are users? (descriptive statistics)

Computed over the 868 worn user-days (72 flagged non-wear days excluded; see data quality report).

| Metric | Mean | Median | Std dev | Min | P25 | P75 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| Total steps/day | 8,271.5 | 7,969.0 | 4,773.0 | 0 | 4,824.8 | 11,055.0 | 36,019 |
| Calories burned/day | 2,353.3 | 2,219.0 | 712.3 | 52 | 1,853.8 | 2,830.5 | 4,900 |
| Sedentary minutes/day | 954.0 | 1,020.0 | 283.2 | 0 | 720.8 | 1,189.0 | 1,440 |
| Total active minutes/day | 246.4 | 257.0 | 106.8 | 0 | 181.0 | 322.2 | 552 |
| Distance/day (km) | 5.9 | 5.6 | 3.7 | 0 | 3.3 | 7.9 | 28.0 |

**Observation:** mean and median are close for every activity metric (within 7%), so unlike many behavioral datasets, a handful of extreme days is not dragging the average away from the typical day. The distribution (see `daily_steps_distribution.png`) is right-skewed with a long tail of very active days, but the bulk of days cluster between roughly 5,000 and 13,000 steps.

**Interpretation:** the average user in this sample logs steps below the commonly cited 10,000-steps/day public-health reference point (mean 8,272; median 7,969), and spends more than half of every logged day (954 of ~1,440 minutes, 66%) sedentary. Sedentary minutes exceed active minutes by roughly 4 to 1.

## 2. How much do users sleep? (descriptive statistics)

Computed over 410 logged sleep-nights from 24 of 33 users (9 users never logged sleep in this export).

| Metric | Mean | Median | Std dev | Min | P25 | P75 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| Minutes asleep | 419.2 (7.0h) | 432.5 (7.2h) | 118.6 | 58 | 361.0 | 490.0 | 796 |
| Minutes in bed | 458.5 (7.6h) | 463.0 (7.7h) | 127.5 | 61 | 403.8 | 526.0 | 961 |

**Observation:** the median night (7.2 hours asleep) sits inside the commonly cited 7-9 hour adult recommendation, but the standard deviation (118.6 minutes, almost 2 hours) shows wide night-to-night variability, and the 25th percentile (6.0 hours) falls below it.

**Caveat on individual averages:** at the per-user level, several users logged very few nights (as few as 1-3 out of 31), producing unreliable personal averages (for example, one user's 1-night average of 1.0 hour, and another's 3-night average of 10.9 hours, are both almost certainly sampling artifacts, not real habitual sleep). 15 of the 24 sleep-logging users have 10 or more logged nights and are the more reliable basis for any individual-level sleep claim; the population-level distribution above (410 nights, pooled) is more robust than any single user's average.

## 3. Statistical tests

Each test follows: hypothesis, method, assumptions, result, business interpretation. Consistent with the project's analytical standards, none of these results are treated as evidence of causation.

### 3.1 Steps vs. calories burned

- **Hypothesis (H0):** no linear relationship between daily steps and daily calories burned.
- **Method:** Pearson correlation, two-sided test.
- **Assumptions:** approximately linear relationship; n=868 is large enough that moderate non-normality is not a major concern, but the result is still sensitive to the small number of very high-step outlier days.
- **Result:** r = 0.567, r² = 0.322, p < 0.001. Reject H0.
- **Interpretation:** steps explain about 32% of the day-to-day variance in calories burned. The relationship is real and expected (more movement burns more energy) but far from the whole story: calories burned also depends on body weight, resting metabolic rate, and non-step activity (cycling, strength training) that this device undercounts in step totals. See `steps_vs_calories.png`.

### 3.2 Steps vs. sleep duration

- **Hypothesis (H0):** no linear relationship between a day's step count and that night's sleep duration.
- **Method:** Pearson correlation, two-sided test.
- **Result:** r = -0.190, r² = 0.036, p < 0.001 (n=410). Reject H0, but the effect is small.
- **Interpretation:** there is a statistically detectable but practically weak negative association: days with more steps trend very slightly toward shorter sleep that night. At r² = 0.036, steps explain under 4% of the variance in sleep duration; this is not a strong enough relationship to build a specific marketing claim like "more activity means better sleep" on its own.

### 3.3 Sedentary minutes vs. sleep duration

- **Hypothesis (H0):** no linear relationship between a day's sedentary minutes and that night's sleep duration.
- **Method:** Pearson correlation, two-sided test.
- **Result:** r = -0.601, r² = 0.361, p < 0.001 (n=410). Reject H0.
- **Interpretation:** this is the strongest relationship found anywhere in this analysis. More sedentary time on a given day is associated with less sleep that night (and, equivalently, less sedentary/more active time is associated with more sleep). Sedentary minutes explain about 36% of the variance in that night's sleep duration, over ten times what step count alone explains (Section 3.2). This does not prove sitting less causes better sleep; both could be driven by a third factor (e.g., overall daily routine, stress, or schedule). It does make sedentary time, not step count, the activity metric most worth featuring in any sleep-related product messaging. See `sedentary_vs_sleep.png`.

### 3.4 Distance vs. calories burned

- **Hypothesis (H0):** no linear relationship between daily distance and daily calories burned.
- **Method:** Pearson correlation, two-sided test.
- **Result:** r = 0.628, r² = 0.395, p < 0.001 (n=868). Reject H0.
- **Interpretation:** the strongest of the four correlations tested, as expected since distance and calories are both direct, mechanical functions of how much a person moved. This is confirmatory (distance and calories should move together) rather than a novel behavioral insight, and is reported for completeness.

### 3.5 Weekday vs. weekend activity

- **Hypothesis (H0):** average daily steps (and, separately, average sedentary minutes) are equal on weekends and weekdays.
- **Method:** Welch's two-sample t-test (unequal variances assumed).
- **Result (steps):** weekday mean 8,288.9 (n=643) vs. weekend mean 8,221.7 (n=225); t=0.163, p=0.871. Fail to reject H0.
- **Result (sedentary minutes):** weekday mean 960.3 vs. weekend mean 936.0; t=1.051, p=0.294. Fail to reject H0.
- **Interpretation:** total daily activity does not differ meaningfully between weekdays and weekends in this sample. What does differ is *when* during the day that activity happens (Section 4). A campaign premised on "weekends are more/less active" is not supported by this data; a campaign premised on "activity timing shifts on weekends" is.

## 4. When are users active? (time-of-day and day-of-week patterns)

### Day of week (worn days only)

| Day | Avg steps | Avg active minutes | Avg sedentary minutes | n days |
|---|---:|---:|---:|---:|
| Monday | 8,488 | 250.0 | 990.5 | 110 |
| Tuesday | 8,885 | 256.6 | 966.9 | 139 |
| Wednesday | 8,158 | 241.4 | 953.8 | 139 |
| Thursday | 8,064 | 236.1 | 919.5 | 135 |
| Friday | 7,821 | 248.2 | 978.3 | 120 |
| Saturday | 8,791 | 263.4 | 927.1 | 115 |
| Sunday | 7,627 | 229.3 | 945.2 | 110 |

Tuesday is the single most active day by steps; Sunday is the least active. This is a mild pattern (a roughly 1,250-step gap between the highest and lowest day, against a population standard deviation of 4,773), consistent with Section 3.5's finding that weekday-vs-weekend totals are not statistically different.

### Hour of day

See `hourly_activity_profile.png`. Two distinct shapes emerge:

- **Weekdays** show two activity peaks: a moderate one around midday (~12:00-13:00) and a larger one in the early evening (~18:00), with a dip in between around 15:00. This is consistent with lunch-break movement and an evening commute or exercise window.
- **Weekends** show one broad peak in the early-to-mid afternoon (~13:00-14:00) and a flatter profile overall, without the sharp evening spike.

**Business interpretation:** users are not simply "more or less active" between weekday and weekend; their activity is scheduled differently. A weekday reminder or prompt timed for late morning or early evening reaches users when they are already moving; a weekend prompt timed similarly would miss the pattern, since weekend activity peaks earlier in the afternoon and evening activity is minimal.

## 5. Device usage frequency

Computed from `device_usage_days` (any day with a logged activity record, out of the 31-day study period), regardless of wear status.

| Tier | Days logged | Users |
|---|---|---:|
| Near-daily use | 28-31 days | 27 (81.8%) |
| High use | 21-27 days | 2 (6.1%) |
| Moderate use | 11-20 days | 3 (9.1%) |
| Low use | 10 days or fewer | 1 (3.0%) |

See `device_usage_frequency.png`. The large majority of users (81.8%) logged activity on nearly every day of the study; a small minority disengaged early or used the device sporadically. Sleep logging is markedly less consistent than activity logging: only 24 of 33 users (72.7%) logged sleep at all, against 33 of 33 for activity. This gap, not overall device abandonment, is the more actionable usage finding: users keep wearing the device for step/activity tracking even when they stop (or never start) using the sleep-tracking feature.

## 6. User segmentation

**Method:** k-means clustering on four standardized per-user features (average daily steps, average sedentary minutes, average active minutes, average daily calories), with the number of clusters (k) chosen by silhouette score over k=2 to k=4 (k capped at 4 given only 33 users; finer splits would produce segments of 2-3 people, too small to be a robust or actionable marketing segment). Full method in `src/bellabeat/segmentation.py`.

**Result:** k=2 had the highest silhouette score (0.342, vs. 0.331 for k=3 and 0.339 for k=4). A silhouette score in the low-0.3s indicates real but moderate separation between groups, not a sharp natural boundary; the two segments below should be read as a useful simplification for messaging purposes, not as a claim that users fall into two hard behavioral types.

| Segment | Users | Avg steps/day | Avg sedentary min/day | Avg active min/day | Avg calories/day | Avg device usage days |
|---|---:|---:|---:|---:|---:|---:|
| Low activity | 12 (36%) | 4,819 | 1,139.8 | 159.1 | 2,163.7 | 27.1 |
| High activity | 21 (64%) | 9,639 | 871.6 | 283.5 | 2,428.8 | 29.3 |

See `user_segments.png` (plotted on two of the four clustering features; the other two, active minutes and calories, follow the same direction).

**Observations:**

- The two segments differ by roughly 2x in average steps and active minutes, and by about 270 sedentary minutes/day (4.5 hours).
- The High-activity segment also logs the device slightly more consistently (29.3 vs. 27.1 average days), though this gap is small relative to the 31-day study window and should not be overstated.
- Average daily calories differ by only about 265 (12%) between segments, much less than the roughly 2x gap in steps. Calories burned depends on body weight and resting metabolism as well as movement, so it is a weaker differentiator between these groups than steps or active minutes are; this is expected, not a data quality issue (see Section 3.1).
- 64% of this sample falls into the higher-activity group. Given the small, self-selected, MTurk-recruited sample (documented in the data quality report), this proportion should not be read as an estimate of what share of Bellabeat's actual customers are highly active.
