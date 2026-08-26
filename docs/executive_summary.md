# Executive Summary

**For:** Urska Srsen, Sando Mur, and the Bellabeat Marketing team
**Question:** What did we learn about how users use smart fitness devices, and what should Bellabeat do with this information?

## The data

Fitabase export of 33 Fitbit users over 31 days (April-May 2016): daily activity, sleep, and hourly usage records. This is a small, self-selected, historical sample with no demographic information; it should be treated as a source of testable hypotheses about Bellabeat's own customers, not as proof about them. Full caveats: `docs/data_quality_report.md`.

## What users are doing

- The typical worn day includes **7,969 median steps** and **954 minutes (66% of the day) sedentary**. Even the more active half of this sample spends the majority of the day sedentary.
- Users **wear the device consistently for activity** (82% logged activity on 28 or more of 31 days) but **not for sleep** (only 73% ever logged sleep at all, and just 15 of those 24 logged it consistently).
- **Total activity does not change between weekdays and weekends** (no statistically significant difference in steps or sedentary minutes), but **when** users are active does shift: weekdays show two activity peaks (midday and early evening), weekends show one broader early-afternoon peak.
- Users split into two behaviorally distinct groups: a **Low-activity segment (36%, ~4,800 steps/day)** and a **High-activity segment (64%, ~9,600 steps/day)**, roughly 2x apart in both steps and active minutes.

## What the data tells us about behavior

The single most important behavioral signal in this analysis is not steps, it is **sedentary time**. Sedentary minutes explain about 36% of the night-to-night variation in sleep duration (a strong, statistically significant relationship), while step count explains under 4%, roughly ten times weaker. Distance and calories move together closely, as expected, but add no new behavioral insight beyond confirming the device measures movement consistently.

This reframes the standard "get more steps" fitness narrative: for this sample, **less sitting**, not **more walking**, is the activity behavior most worth building a message around, particularly for anything connected to sleep.

## What Bellabeat should do

Five evidence-based recommendations, each fully detailed with its supporting finding in `docs/insights_and_recommendations.md`:

1. **Market movement reminders as a sleep-quality feature**, not just an activity nudge, since sedentary time (not steps) is what tracks with sleep in this data.
2. **Lead wellness content with "sit less," not "walk more,"** since sedentary time dominates the day even for already-active users.
3. **Run a dedicated engagement push for sleep logging**, since consistent activity tracking does not carry over to consistent sleep tracking on its own.
4. **Time notifications to actual activity windows** (weekday midday/evening, weekend early afternoon) instead of a generic weekday/weekend split, since overall activity level does not differ by day type, but timing does.
5. **Replace a universal step goal with a personalized, baseline-relative target**, since this sample splits into two groups roughly 2x apart in typical activity, for whom one fixed number would be either discouraging or too easy.

## Bottom line

This dataset does not support broad claims about "how people use fitness trackers" in general; it supports a specific, useful redirection for Bellabeat: **prioritize sedentary-time and sleep-consistency messaging over step-count messaging**, and **personalize both goals and notification timing** rather than applying one standard to all users. These are testable next steps against Bellabeat's own user base, not final conclusions.
