# Smart Mobility Le Mans

Decision support pipeline for the question: *if Le Mans Métropole had limited resources to improve its public transport, where and when should it intervene?*

- **Static pipeline** (monthly): SETRAM GTFS -> `data/gtfs_static/` (stop frequency, routes, commune supply vs. population)
- **Real-time pipeline** (every 15 min): GTFS-RT delays + alerts -> `data/history/` and `docs/data/current_state.json`
- **Dashboard**: GitHub Pages from `/docs`

Limits: population is only a proxy for demand (no open ridership data); GTFS-RT has no archive, so patterns need weeks of accumulated history.
