# Key Insights and Marketing Recommendations

**Phase covered:** Act
**Built on:** `docs/analysis_findings.md` (Analyze phase) and `docs/data_quality_report.md` (data limitations)
**Audience:** Urska Srsen (Co-founder, Chief Creative Officer), Sando Mur (Co-founder), Bellabeat Marketing Analytics Team, Bellabeat Marketing Leadership

Every recommendation below traces to a specific, numbered finding in `docs/analysis_findings.md`. None are speculative additions beyond what the data supports, and none claim causation from the underlying correlational findings.

---

## Recommendation 1: Feature and market a "sit less" reminder around sleep benefits, not just activity

**Finding:** Sedentary minutes are far more strongly associated with that night's sleep duration (r = -0.601, r² = 0.361) than step count is (r = -0.190, r² = 0.036). See Analysis Findings, Section 3.2-3.3.

**Interpretation:** Whatever is driving the sleep relationship in this data, it tracks with how much of the day was spent sedentary far more than with how many steps were taken. A step-count goal is not the most relevant activity lever for a sleep-focused message; time spent sitting is.

**Marketing Opportunity:** Bellabeat positions itself around holistic wellness, not just step-counting. A sedentary-time-and-sleep message is a natural fit for that positioning and is differentiated from competitors who lead with step counts.

**Recommendation:** Prioritize and market Bellabeat's break-up-sitting / movement reminders explicitly as a sleep-quality feature ("less sitting today, better sleep tonight"), rather than bundling it as a generic activity nudge. Pair this in-app with the "hourly movement" pattern already common in wearables, but frame the value proposition around sleep, which this data ties to sedentary time far more strongly than to steps.

**Expected Impact:** More users opting into and acting on movement reminders (a feature promoted for the outcome the data actually supports), and a sleep-and-activity message that is differentiated from step-focused competitor marketing.

---

## Recommendation 2: Lead wellness content with "sit less," not "walk more"

**Finding:** The average worn day is 66% sedentary (954 of ~1,440 logged minutes); even users in the higher-activity segment average 872 sedentary minutes/day, 14.5 hours. See Analysis Findings, Sections 1 and 6.

**Interpretation:** Sedentary time dominates the day for essentially everyone in this sample, including already-active users. Being "active" in this dataset means a shorter sedentary block, not the absence of one.

**Marketing Opportunity:** A wellness-education angle ("most of your day is still sedentary, here's how small changes help") is credible and true for nearly this entire sample, including people who already think of themselves as active, widening the addressable audience for this message beyond people who see themselves as needing to "get fit."

**Recommendation:** Build editorial/in-app content around reducing sedentary time in small, achievable increments (e.g., standing breaks, short walks between tasks) rather than solely promoting step-count milestones.

**Expected Impact:** Content that resonates with both the low- and high-activity segments identified in this analysis, since both groups spend the majority of their day sedentary; potential to increase content engagement and time-in-app.

---

## Recommendation 3: Build a dedicated sleep-logging engagement push, separate from activity engagement

**Finding:** 33 of 33 users logged activity, but only 24 of 33 (72.7%) ever logged sleep, and only 15 of those 24 logged sleep on 10 or more nights. See Analysis Findings, Sections 2 and 5.

**Interpretation:** Keeping a device on for step-tracking does not automatically translate into consistent sleep-tracking use. Sleep-feature engagement is a distinct behavior that needs its own prompt, not an assumed side effect of general device usage.

**Marketing Opportunity:** Bellabeat's product line (including the Leaf and the app's wellness scoring) depends on sleep data to deliver its full value; incomplete sleep data means users see a less complete, less compelling picture of their own health, which likely dampens perceived product value.

**Recommendation:** Run an engagement campaign or in-app prompt specifically targeting users who are active but not consistently logging sleep, explaining what the sleep feature adds and nudging nightly wear. Treat this as a distinct retention lever from general "wear your device" messaging.

**Expected Impact:** Higher and more consistent sleep-log coverage, which both improves the personalized insights Bellabeat can offer back to the user (a retention driver) and gives Bellabeat a more complete internal picture of user behavior for future analysis.

---

## Recommendation 4: Time notifications to actual behavior windows, not a generic weekday/weekend split

**Finding:** Total daily steps and sedentary minutes do not differ significantly between weekdays and weekends (steps: p = 0.871; sedentary minutes: p = 0.294), but the time of day activity happens does shift: weekdays show two activity peaks (midday and early evening), weekends show one broader early-afternoon peak. See Analysis Findings, Sections 3.5 and 4.

**Interpretation:** Users are not more or less active on weekends, so a marketing assumption of "weekend = more free time = more activity" is not supported here. What changes is *when* they move.

**Marketing Opportunity:** A notification or reminder timed for a moment users are typically inactive is easy to ignore or dismiss; one timed to an actual activity window is more likely to land when the user is already receptive to a movement-related message.

**Recommendation:** Schedule activity-related push notifications and in-app prompts around the observed weekday peaks (late morning, early evening) and the weekend peak (early-to-mid afternoon), rather than using one fixed schedule across all seven days.

**Expected Impact:** Improved notification response and click-through rates, and less notification fatigue from prompts sent at times users are reliably inactive.

---

## Recommendation 5: Replace the universal step goal with a personalized, baseline-relative target

**Finding:** Median daily steps (7,969) sit below the commonly cited 10,000-step reference point, and the sample splits into a Low-activity segment (36% of users, ~4,819 steps/day) and a High-activity segment (64%, ~9,639 steps/day) that differ by roughly 2x in steps and active minutes. See Analysis Findings, Sections 1 and 6.

**Interpretation:** A single fixed step target is a mismatch for a population this spread out: it would be discouragingly out of reach for the Low-activity segment and insufficiently challenging for much of the High-activity segment.

**Marketing Opportunity:** Bellabeat can differentiate on personalization, positioning itself against one-size-fits-all step-counting competitors by meeting users at their own baseline rather than a generic public-health number.

**Recommendation:** Set and market activity goals relative to each user's own recent baseline (e.g., "walk 10% more than your usual day") rather than a fixed step count, and reflect this personalization explicitly in marketing creative aimed at users who feel discouraged by generic fitness-tracker goals.

**Expected Impact:** Higher goal-completion rates and lower early disengagement among lower-baseline users, sustained challenge for higher-baseline users, and a differentiated brand message for user acquisition.

---

## Limitations that apply to every recommendation above

These are carried forward from `docs/data_quality_report.md` and should be read alongside every recommendation:

1. **Sample size and composition:** 33 users, self-selected into an Amazon Mechanical Turk survey in 2016. No demographic data (age, gender, health status) is available, and Bellabeat's target market is women specifically, whose representation in this sample is unknown. Treat every finding as a hypothesis to validate against Bellabeat's own user data, not as a conclusion about Bellabeat's customers.
2. **Time period:** data is from April-May 2016. Device capability, app design, and user behavior around wearables have changed materially since; absolute levels (e.g., "8,271 average steps") may not hold today even if directional patterns (e.g., sedentary time mattering more than steps for sleep) still do.
3. **Correlation, not causation:** every relationship reported (steps-calories, steps-sleep, sedentary-sleep, distance-calories) is an association observed in 31 days of one small sample. None of it should be presented externally as a proven causal claim (e.g., do not market "reducing sedentary time improves your sleep" as a clinical guarantee; market it as an observed pattern worth trying).
4. **Segmentation strength:** the two-segment split (Recommendation 5) has a silhouette score in the low 0.3s, indicating real but moderate separation, not a hard behavioral boundary. Use it to inform messaging tiers, not to rigidly categorize individual users.
5. **Missing weight and limited heart-rate data:** only 8 of 33 users logged weight and only 14 of 33 have heart-rate data, both too sparse to support population-level claims; neither was used as a basis for any recommendation above.
