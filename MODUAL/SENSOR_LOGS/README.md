# MODUAL / SENSOR_LOGS — GitHub Current State

SOURCE_DIRECT: D:\\SENSOR_LOGS

- Bulk and live sensor source bytes remain on their original local/provider carriers.
- GitHub stores source digest, byte count, modification time, and CSV header only.
- `BULK_LATEST_CURRENT.csv` and `LIVE_LATEST_CURRENT.csv` are compatibility names for **header-only** snapshots; they do not contain a latest sensor row.
- `live/` contains a header-only compatibility carrier, not a copy of the raw live source.
- `MODUAL_PARAMETER_CURRENT.json` is compact metadata/state. Additive provenance fields are preserved by the sync helper.
- `source/` contains executable control files.

## Execution and export gates

- `telemetry_buffer_sync.py` with no arguments or `--once` performs one finite observation and exits; this is the safe Scheduled Task default.
- `--loop` is explicit long-running daemon mode and is used by `START_TELEMETRY_SYNC.bat`.
- Cloud export requires `SOL_ENABLE_SENSOR_CLOUD_EXPORT=1`.
- GitHub state export requires `SOL_ENABLE_SENSOR_GITHUB_PUSH=1`; it publishes metadata and headers only, never sensor rows.
- A valid CSV and a successful read-only observation do not prove that the live sensor stream is running.

GitHub is used as Law/State, not as the bulk telemetry store.
