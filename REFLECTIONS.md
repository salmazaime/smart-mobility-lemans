# Reflections: Smart Mobility Le Mans

## 1. Easy vs. hard sub-questions
Easy: which routes are late right now, and which stops are busiest on paper (both have data). 
Hard: where demand is highest, when delays repeat, and any prediction, because there is no ridership data and no history.

## 2. Why the static feed doesn't refresh every 15 min
It only changes when SETRAM publishes a new timetable, every few months. Running every 15 minutes would just re-download the same zip and make useless commits.

## 3. Auto-typed ID columns
If one file reads `stop_id` as numbers and another as text (like `FLEX-381`), the merge fails or silently matches nothing. Stops lose their data and nothing looks broken. Using `dtype=str` fixes it.

## 4. Per-route vs. per-stop logging
Per-stop is about 5,000 x 96 x 84 = 40 million rows (too big for git). Per-route is about 30 x 96 x 84 = 250,000 rows. The downside is that you can't tell which specific stop is the problem, because averaging hides it.

## 5. Better than green-early / red-late
Use a scale centred on on-time: grey near 0, red for late, blue for early. Being very early is also a problem because people miss the bus. On my dashboard route 34 is about 120 s early and shows up bright green like the best route, but a planner should check its timetable or driver pacing instead.

## 6. The scheduling mismatch
Static every 15 min wastes runs because nothing changes. Real-time monthly is useless because delays change by the minute and one snapshot misses almost everything. The schedule should match how fast the data changes.

## 7. Sanity check of one delayed route
The most delayed route was route 5, with an average delay of about 80 s, in the snapshot from 2026-10-21 09:15 UTC (11:15 in Le Mans). That's mid-morning, not rush hour, and the dashboard showed 0 active alerts, so nothing obvious explains it. 80 s is also only a bit over a minute, so it's not a real crisis. My guess is normal small delays or a few stops pulling the average up, not a disruption. (Check the SETRAM site for route 5 to confirm.)

## 8. Where population misleads
Population shows where people sleep, not where they travel. A small commune with a hospital, university, station or business park gets lots of trips. A big commuter suburb where everyone drives gets few.

## 9. My supply metric
Metric: scheduled stop-visits per 1,000 residents.
It looks wrong for La Chapelle Saint Aubin. It ranks first with 1010 per 1,000, but it only has 2,319 residents and 53 stops. That is probably because stops are assigned to the nearest commune centre (so stops on the edge of le mans end up counted here)..this inflates it. The same rule deflates Le mans, which ranks only 10th (153.8) even though it has the most service (329 stops, 22,900 visits/day) and the main station. Fay, Chaufour-Notre-Dame and Fatines are flagged orange (!) because one stop gives 30%+ of their supply (so their numbers are also not reliable).

## 10. Stop-level delays without a huge file
Dont store raw rows. Keep running totals per stop, hour and day-type (count, sum, max, number over 180 s)...thats about 86,000 rows, and the file stays the same size forever.
