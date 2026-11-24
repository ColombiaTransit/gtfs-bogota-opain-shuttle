# Step 64 — Public OPAIN Bus Satélite: Nov 24 OpenStreetMap export comparison

**Date of OSM snapshot:** 2026-11-24 05:44 UTC. **Input:** owner-provided Overpass Turbo JSON `export (7).json`, bounding box `4.675,-74.175,4.715,-74.115`. OSM data © OpenStreetMap contributors, ODbL. See the [central machine-readable source register](../data/opain-public-shuttle/source-register.json).

## What was actually returned

- **4,716** OSM elements: **435 nodes, 4,272 ways, 9 relations**. Of the roads, **4,266 ways have a `highway` tag** and **273 elements are tagged `highway=bus_stop`**. Many belong to Bogotá SITP, not OPAIN.
- **No stop or route relation explicitly named OPAIN / Bus Satélite / Bus Aeroportuario**, and no source objects specifically tagged `TC1`, `TC2`, `TC3` or `NEAA`. This does not prove that the free shuttle or its stops do not exist; they are simply not identifiable as such in the queried OSM data.
- Several named *SITP* bus stops and airport terminal/cargo polygons are nevertheless useful landmark candidates.

## Closest named public transport OSM landmarks to previously archived MapVX `Bus Satélite` points

| Area | OSM object ID | Exact OSM label/ref | From original MapVX POI | Interpretation |
| --- | --- | --- | --- | --- |
| T1 | [node/14202289243](https://www.openstreetmap.org/node/14202289243) | Aeropuerto Eldorado, SITP 377A05 | 149 m | Separate SITP, NOT proved OPAIN |
| T1 | [node/14252560576](https://www.openstreetmap.org/node/14252560576) | Aeropuerto Eldorado, SITP 377B05 | 186 m | Separate SITP, NOT proved OPAIN |
| T1 | [node/997742232](https://www.openstreetmap.org/node/997742232) | Unnamed bus platform | 191 m | Unattributed, NOT proved OPAIN |
| T2 | [node/14202289242](https://www.openstreetmap.org/node/14202289242) | Puente Aéreo, SITP 383A05 | 99 m | Separate SITP, NOT proved OPAIN |
| T2 | [node/14202289245](https://www.openstreetmap.org/node/14202289245) | CAC, SITP 382A06 | 134 m | Separate SITP, NOT proved OPAIN |
| T2 | [node/4991432624](https://www.openstreetmap.org/node/4991432624) | Puente Aéreo, SITP 380A05 | 298 m | Another SITP location, NOT proved OPAIN |
| Near NEAA | [node/6743732547](https://www.openstreetmap.org/node/6743732547) | Aeronáutica Civil, SITP 383A06 | N/A | Relevant general area, no independent OPAIN stop proof |

All figures are straight-line distances measured between the **existing MapVX source POI** at T1 (4.697749,-74.142048) or T2 (4.693750,-74.135236) and the exported OSM coordinates. Their actual public bus boarding poles are **not** proven by these numbers.

## Buildings, roads and what is still missing

- T1 terminal: [way/67200836](https://www.openstreetmap.org/way/67200836), `Terminal T1`.
- Two objects are named `Terminal de Carga El Dorado`: [way/24198658](https://www.openstreetmap.org/way/24198658) and [way/65866132](https://www.openstreetmap.org/way/65866132). The names do **not** tell us which is TC1 and which is TC2/3; their shape-centroid coordinates are **not** stops.
- Source MapVX T1 `Bus Satélite` POI is around **10 m** from a one-way `Llegadas` road segment [way/609023005](https://www.openstreetmap.org/way/609023005). T2 MapVX POI is around **1 m** from an OSM one-way service road [way/1025720596](https://www.openstreetmap.org/way/1025720596). Neither proximity is boarding confirmation; no automatic curbside snap is authorized.
- The requested wide Overpass export covers many city roads, but it is not a validated full routable OSM PBF for GraphHopper, and it contains no source-confirmed OPAIN driving line, direction at each stop or stop-to-stop runtimes.

## Specific 7-stop decision

Keep the official circular sequence and source labels from [Step 63](step-63-opain-public-shuttle-baseline.md). **After the owner confirmed two T1 shuttle stops**, three MapVX-based coordinates have been taken over **provisionally** in the central register: distinct T1 Puerta 2 and Puerta 11, plus T2. All have `physical_stop_location_reviewed=false`; the T1 Puerta 11 match is based only on a MapVX bus-route cue near Acceso 1, not a labelled bus-stop POI. The other four stop coordinates remain null. **None of these three locations is independently confirmed as OPAIN curbside boarding from the OSM export.**

**Next source task:** identify the T1 international Puerta 2 / national Puerta 11 curbside boarding locations and the real T2 stop using operator stop signs or public-frontage imagery; match TC1, TC2/3, NEAA and Carrera 103 against the official operator diagram and road side/direction. After confirmation, run the already available OSM road profile in GraphHopper to obtain a candidate circular `shapes.txt` and realistic leg times. The known 15-vs-20-minute frequency discrepancy remains open.

**No passenger-ready GTFS generated; three provisional source-backed coordinates assigned, four remain missing, no Pathways changes.**
