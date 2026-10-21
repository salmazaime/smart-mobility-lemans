# Reflections — Smart Mobility Le Mans

> Items marked **[YOUR OBSERVATION]** depend on your own live output. Fill them in after the pipeline has run. Everything else is a ready answer; reword it in your own voice.

## 1. Easy vs. hard sub-questions (before building)
**Easy:** "which routes are late right now?" (live delay data exists) and "which stops are busiest on paper?" (static schedule exists).
**Hard:** "where is demand highest?" (no open ridership data, only a proxy), "when do delays recur?" (no GTFS-RT archive, needs weeks of my own collection), and any prediction.

## 2. Why the static feed doesn't refresh every 15 minutes
The static GTFS only changes when SETRAM publishes a new timetable (every few months), so polling every 15 minutes would re-download and re-process an identical 2.4 MB zip thousands of times, produce empty commits, and waste runner time and politeness toward the data provider.

## 3. What breaks when ID columns are auto-typed independently
If pandas reads `stop_id` as integers in one file and as text in another (because one file happens to contain only numeric-looking IDs and the other has values like `FLEX-381`), the merge either raises a dtype error or, worse, silently matches nothing. Stops would lose their coordinates or frequencies, and every downstream number would be wrong without any visible failure. Reading everything with `dtype=str` makes IDs consistent labels, not numbers.

## 4. Per-route vs. per-stop logging over a semester
Per-stop: ~5,000 rows x 96 snapshots/day x 84 days ≈ **40 million rows** (order of 10^7–10^8; far too heavy for a git-tracked CSV).
Per-route: ~30 routes x 96 x 84 ≈ **250,000 rows** (order of 10^5).
The per-route choice makes it harder to answer **"which specific stops or segments suffer repeated delays?"**, e.g. a planner deciding where to build a bus lane or move a stop. Averaging over a route hides a single bottleneck.

## 5. Alternative to the green-early / red-late encoding
Use a **diverging scale centred on on-time**: neutral (grey) near 0 s, red for late, **blue/purple for early**, with a tolerance band (for example −60 s to +180 s counts as on time). A viewer under the original rule sees "very early" as the best route and would ignore it. Under mine, a route running far ahead of schedule stands out as a problem (passengers miss the bus), so the planner would investigate timetable padding or driver pacing on that route rather than treating it as a success.

## 6. Both halves of the scheduling mismatch
- Static every 15 min: wasteful. The source changes at most every few months, so nearly every run recomputes identical data and clutters the history with empty or no-op commits.
- Real-time monthly: useless. Delays change minute to minute and the live feed has no history, so one snapshot a month would miss almost every disruption and make "current status" and any recurring-pattern analysis meaningless.
The cadence must match the **rate of change of the source** and the **decision it supports**.

## 7. Sanity check of one delayed route
**[YOUR OBSERVATION]** Route: ____ | Avg delay shown: ____ s | Max: ____ s | Time of day: ____.
What I compared it with (SETRAM site, rush hour, roadworks, event): ____.
Did it match? ____. My best guess if not (real disruption / data artifact such as a few extreme stop-times or a trip with stale delay values / off-hours noise): ____.
*Tip: a low-trip-count route at night with one large delay is usually an artifact of averaging few observations, not a real crisis.*

## 8. Where population misleads as a demand proxy
A commune with few residents but a **major employer, hospital, university, station, shopping area or event site** attracts many trips (Le Mans-area example: the 24 Heures du Mans circuit area in Mulsanne/Arnage on race week, or any commune hosting a large business park). Conversely, a large commune full of **car-owning commuters** or a dormitory suburb can have high population but low transit demand. Population measures where people sleep, not where they travel.

## 9. My supply metric and a commune where it misleads
**Metric:** scheduled stop-visits per 1,000 residents (sum of weekday scheduled stop-times at stops assigned to the commune, divided by population x 1,000).
**Commune where it looks wrong:** **[YOUR OBSERVATION: pick from your commune_supply.csv]**.
Likely candidates to check in your output:
- **Le Mans** itself: 149k residents but assigning each stop to the *nearest commune centroid* sends many stops on the city's edges to Coulaines, Allonnes, Arnage etc. This inflates those suburbs and deflates Le Mans.
- Any commune with the **(!) flag** on the dashboard, where one interchange/terminus/depot provides 30%+ of supply: it looks very well served although most residents live far from that stop.
- Communes with **0 stops** (small rural ones): ranked last, but that may be a genuine gap or just the nearest-centroid rule.
Explain with what you know about the commune (e.g. its size, whether the stop is a terminus, whether residents are near the line).

## 10. Aggregating stop-level delay events without blowing up the file
Keep per-stop data only as **running aggregates per (stop, hour-of-day, day-type) bucket** instead of raw rows: for each bucket store count, sum of delay, max delay and number of delays over a threshold (e.g. > 180 s), updating a small `stop_delay_summary.csv` each run. That is ~1,800 stops x 24 hours x 2 day-types ≈ 86,000 rows total, constant size however long it runs. Optionally, log raw stop-level rows **only for events over the threshold**, and roll them up weekly then discard the raw rows.

## 11. Reflection 1 predictions vs. what I found
**Answerable today:** where scheduled service is concentrated, which routes are currently delayed, whether an alert is active.
**Needed judgment calls:** choosing population as the demand proxy, choosing the metric (per 1,000 residents), the nearest-centroid commune assignment, the on-time definition and colour encoding, and picking one representative weekday.
**Needs weeks of history:** recurring delay patterns by hour/day, which routes are chronically late, and any prediction.
**Compared to my guess:** **[YOUR OBSERVATION: what surprised you, e.g. how noisy the delay data was, or how strongly the metric favoured small suburbs.]**
