# Step 63 — OPAIN public Bus Aeroportuario / Bus Satélite (landside), 2026 baseline

**2026-11-23.** The owner parked indoor Pathways and selected the **public/landside OPAIN shuttle** as the active next research workstream. Keep the shuttle in this private repository while locating the terminal-area stops, as agreed in [Step 11](step-11-airside-shuttle.md). This is a **conventional road bus service**, not an indoor Pathway or the separately unresolved behind-security shuttle.

## Current primary sources

1. [Current airport transport page](https://eldorado.aero/transporte/como-llegar-al-aeropuerto) explicitly says the public T1/T2 shuttle runs **daily 04:00 to midnight** and links to the official [7-stop shuttle schematic](https://static.eldoradoaero.com/web/pdf/transporte/paraderos-bus-aero2.pdf). That directly linked PDF says **every 20 minutes**.
2. [OPAIN's 2026 electric fleet announcement](https://eldorado.aero/comunicados/el-dorado-renueva-el-servicio-de-bus-aeroportuario-gratuito-con-vehiculos-100-electricos) says public shuttle between T1, T2 and cargo terminal, daily, with **approximately 15-minute** headways. Its body writes `12:00 p.m.`, inconsistent with the current transport page's explicit midnight notation; adopt the current transport page's **04:00–00:00**, and keep the frequency discrepancy visible.
3. The [historical OPAIN operational procedure GOP-PR-0034 v12](https://www.opain.co/archivos/gop-pr-0034-procedimientoserviciobussatliteaeropuerto.pdf) (June 2020) gives a similar circular stop sequence but lists international **Puerta 8** and conditional **TC1** visits. These old operational conditions are NOT presumed still valid in 2026.

## Current official schematic: seven *unique* stop places, circular order

| No. | Current operator label | Confidence |
| --- | --- | --- |
| 1 | T1, Llegadas Internacionales, **Puerta 2** | Label/sequence official; curbside stop coordinates not yet verified |
| 2 | T1, Llegadas Nacionales, **Puerta 11** | Label/sequence official; coordinates not yet verified |
| 3 | Terminal de Carga 1 (TC1) | Label/sequence official; current stopping exceptions unresolved |
| 4 | Terminal de Carga 2 y 3 | Label/sequence official; coordinates not yet verified |
| 5 | Edificio Aeronáutica Civil (NEAA) | Label/sequence official; coordinates not yet verified |
| 6 | Carrera 103 / Antigua Zona de Aviación General | Label/sequence official; coordinates not yet verified |
| 7 | Terminal 2 (Puente Aéreo) | Label/sequence official; coordinates not yet verified |

The diagram closes back to stop 1. This is a *schematic*, not a geographic driving shape. A repeat of stop 1 may be included as a terminal `stop_times.txt` entry for a complete loop; **do not create an eighth unique physical stop**. **Project decision (2026-11-24):** current OPAIN stop names and order are canonical. Moovit may be outdated; its labels and service claims must not overwrite the OPAIN records or create an eighth physical stop.

## Existing internal mapping evidence (do not duplicate)

[Step 11 source route analysis](step-11-full-route-analysis.md) already recorded:

- MapVX `Bus Satélite T1` catalogue point: **4.697749, -74.142048** (near a repeated T1→T2 bus instruction).
- MapVX `Bus Satélite T2` catalogue point: **4.693750, -74.135236** (near a T2→T1 bus cue).
- Several original route instructions mention public doors 1 and 11. A bus *instruction* is not a validated boarding pole, and such cues must not be confused with an airside shuttle.

**Owner confirmation (2026-11-24): T1 has two distinct public shuttle stops, Puerta 2 and Puerta 11.** We adopted separate MapVX-backed **provisional** coordinates for both T1 stop IDs and the T2 stop ID in the [structured source register](../data/opain-public-shuttle/source-register.json): Puerta 2 = `4.697749,-74.142048` (named Bus Satélite T1 POI); Puerta 11 = `4.697610,-74.140097` (distinct MapVX bus cue by Acceso 1, Nivel 1); T2 = `4.693750,-74.135236` (named Bus Satélite T2 POI). **Puerta 11 assignment is low-confidence**, since its MapVX point is a route step cue rather than a named shuttle-stop POI. All three retain `physical_stop_location_reviewed=false`; they are research inputs, not certified curbside boarding positions. Of the four nonterminal stops, **three now have provisional existing SITP platform coordinates** (current OPAIN stop nos. 4, 5 and 6); **TC1 still has no valid stop coordinate**. OPAIN use of the SITP kerbs remains a working hypothesis.

## GTFS modeling decision

- Separate **public** bus `route_type=3`, branded OPAIN Bus Satélite, with **one directed circular route** unless actual operations prove variants.
- Free service, daily operating window **04:00 to 24:00 America/Bogota**; no exact departure times are claimed.
- **Headway unresolved**: current linked official PDF **20 min**, 2026 OPAIN press release **~15 min**. Use neither as a confirmed exact timetable. If a research-only timetable scenario is needed, label its assumed headway explicitly.
- Do not publish a passenger-ready `stops.txt` based solely on provisional MapVX/SITP coordinates. Preserve the two *distinct* T1 stop IDs. No `shapes.txt` inferred from the schematic; no stop-to-stop running times invented from MapVX gate-to-gate itinerary summaries.
- Keep OPAIN public route separate from security-restricted T1↔T2 transfer hypotheses and from the indoor Pathways research.
- A GTFS generator, MobilityData validation and OTP routing checks follow after at least operator-stop geolocation, credible road shape and segment times are available.

> **2026-11-24 update:** [Step 64 OSM Overpass export comparison](step-64-opain-public-shuttle-osm-comparison.md) found SITP airport stops and cargo-area landmarks, but no OSM stop explicitly identified as OPAIN's public shuttle. All seven official OPAIN boarding locations remain physically unverified, though six now have source-backed provisional coordinates (three MapVX and three SITP).

**Status (2026-11-24):** seven official OPAIN stop records, **six provisional source-backed coordinates** (two distinct T1 and T2 from MapVX, stops 4–6 from SITP OSM), **one missing curbside stop (TC1)**. The owner considers OPAIN/SITP shared stops likely, but these are still working assumptions, not independently confirmed OPAIN boarding. No GTFS trips generated, no Pathways change, no release.
