# OPAIN public Bus Satélite — private GTFS prototype v0

**Research-only, NOT FOR PASSENGERS, NOT a public release.** This prototype deliberately combines official OPAIN stop labels with owner-authorized *provisional* positions and *modelled* times. It does **not** certify OPAIN's actual timetable or boarding platforms.

## Inputs and fixed decisions

- Existing central input: [`data/opain-public-shuttle/source-register.json`](../../data/opain-public-shuttle/source-register.json), maintained from official OPAIN and the 2026-11-24 OSM/MapVX investigation. The **two distinct T1 stops** plus TC1, TC2/3, NEAA, Carrera 103 and T2 remain seven separate GTFS stop IDs in current OPAIN circular order.
- OPAIN names are authoritative; **SITP names/numbers and older Moovit names are NOT used as `stop_name`**.
- T1 Puerta 2, T1 Puerta 11 and T2 positions are provisional MapVX data. Stop 4, 5 and 6 positions are provisional OSM SITP locations, based on the owner's shared-stop assumption. None are claimed verified OPAIN boarding poles.
- **TC1:** Street View March 2025 shows explicit *TC1* lettering under cargo access **11** at approximately camera position `4.6939551, -74.1386152`. This is **not an independently verified OPAIN boarding stop**. The input register continues to set `stops[2].lat/lon=null`, and the generator will **refuse to build unless the operator explicitly opts in** to this test-only camera-coordinate substitution. The TC1 source address is *not* T1 passenger terminal Puerta 11.
- OPAIN transport page says **04:00–24:00 America/Bogota daily**, official directly linked schematic **20 minute** headway, separate 2026 press announcement **approximately 15 minutes**. Default `--headway-minutes 20` is a selectable **what-if**, not a verified timetable.
- The default no-server fallback can still model running times using straight-line distance × **1.4 detour factor**, **15 km/h** and **20 seconds boarding dwell**. The GitHub Actions workflow now uses **GraphHopper OSM road geometry and profile=bus** for all seven directed legs, and its computed travel durations (still road-model estimates, not observed times). It emits `shapes.txt`, `shape_id` and `shape_dist_traveled`. No artificial straight-line links are permitted across disconnected road segments.

## Run locally

```bash
python -m unittest discover -s tests -p 'test_opain_public_shuttle.py' -v

python scripts/opain_public_shuttle/build_gtfs.py \
  --allow-tc1-camera-reference \
  --headway-minutes 20 \
  --start-date 20261124 --end-date 20271231 \
  --output inspection-results/opain-public-shuttle/OPAIN-PUBLIC-SHUTTLE-PROVISIONAL-NOT-FOR-ROUTING.zip
```

## Real road shapes from existing private GraphHopper

The workflow first reads the organization variable `vars.GRAPHHOPPER_URL` (private, never hardcoded) and sends seven **POST /route** requests using the available `bus` profile, official OPAIN stop order and GeoJSON coordinates:

```json
{
  "profile": "bus",
  "points": [[-74.142048, 4.697749], [-74.140097, 4.697610]],
  "points_encoded": false,
  "instructions": false,
  "calc_points": true,
  "elevation": false
}
```

As in the earlier ColombiaTransit bus routing workflows, the client sends `Content-Type: application/json`, `Accept: application/json`, a browser-like `User-Agent`, and optional Cloudflare Access headers from `CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET` if configured. The private URL is never echoed or stored in artifacts.

```bash
export GRAPHHOPPER_URL="YOUR_PRIVATE_GRAPH_HOPPER_BASE_URL"
python scripts/opain_public_shuttle/graphhopper_bus_shape.py \
  --allow-tc1-camera-reference \
  --output inspection-results/opain-public-shuttle/graphhopper-bus-route.json
python scripts/opain_public_shuttle/build_gtfs.py \
  --allow-tc1-camera-reference \
  --graphhopper-routes inspection-results/opain-public-shuttle/graphhopper-bus-route.json \
  --output inspection-results/opain-public-shuttle/OPAIN-PUBLIC-SHUTTLE-PROVISIONAL-NOT-FOR-ROUTING.zip
```

GraphHopper geometry and the seven leg durations are saved as JSON plus GeoJSON for review. The generator refuses to accept different stop coordinates, missing legs or a non-`bus` profile. Per-leg stop snaps >100m are reported; >500m are rejected. Consecutive legs must join within 5m at their directed road snap, otherwise the shape is rejected instead of drawing an artificial gap. **Routing does not verify OPAIN boarding, published timetables, or special airport circulation permissions.**

The output ZIP includes these eight base GTFS files, plus **`shapes.txt` when built with `--graphhopper-routes`**:

`agency.txt`, `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`, `frequencies.txt` and `feed_info.txt`.

The accompanying `*.manifest.json` (separate from the GTFS ZIP) clearly documents the camera-coordinate substitute, unconfirmed platforms, headway discrepancy and modelled timings. The resulting GTFS is a **syntax/OTP research prototype only**. It is not suitable for public journey planning.

## GitHub Actions

The workflow [`build-opain-public-shuttle-private.yml`](../../.github/workflows/build-opain-public-shuttle-private.yml) runs source and GraphHopper fixture tests, queries the private road server, creates a shape-enabled GTFS ZIP, and runs the **MobilityData GTFS validator**. All generated content is uploaded as a **private Actions artifact retained for 7 days**, called `opain-public-shuttle-INTERNAL-PROVISIONAL-NOT-FOR-ROUTING`. This workflow never creates a GitHub release or commits the output GTFS ZIP.

Passing structural validation does **not** mean any of the seven physical bus boarding spots, actual travel times, on-the-ground service headway or public eligibility has been verified.

## Remaining before a release

1. Determine the **actual TC1 curbside** platform and replace the Street View camera substitute.
2. Verify OPAIN really uses the assigned SITP boarding platforms at stops 4–6, and revisit the weak MapVX assignment of T1 Puerta 11.
3. Get an actual direction-correct road line and leg times with GraphHopper/OSM, avoiding the invented straight-line scenario.
4. Reconcile OPAIN's **20-minute schematic** vs **approximately 15-minute press announcement**, verify operational times and possible TC1 stop exceptions.
5. Inspect MobilityData notice types and the output OTP itinerary, then seek explicit separate approval before any public GTFS release.

The airside transfer shuttle, indoor Pathways and the separately owned flight GTFS remain **unchanged**.
