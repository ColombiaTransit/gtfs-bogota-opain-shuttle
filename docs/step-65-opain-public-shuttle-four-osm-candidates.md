# Step 65 — Four remaining public OPAIN Bus Satélite stops: OSM location candidates

**2026-11-24.** Follow-on to [Step 64's complete user-provided OSM export](step-64-opain-public-shuttle-osm-comparison.md). Target only the four **remaining public/landside OPAIN shuttle stop places** after retaining two separate T1 stops and the existing T2 MapVX candidate. No new Pathways or secondary/airside shuttle work.

## Source triangulation and exact research-only coordinates

| Official 2026 stop no. / name | Existing OSM object | Candidate latitude / longitude | Meaning |
| --- | --- | --- | --- |
| 3 — TC1, Terminal de Carga 1 | [way/24198658](https://www.openstreetmap.org/way/24198658), Terminal de Carga El Dorado | 4.69363818, -74.14064776 | **Building geometry centroid only**, not a bus stop; older operator route diagram suggests this first cargo area, but OSM name does not certify it as TC1 |
| 4 — TC2 y 3, Terminal de Carga 2 y 3 | [node/14202289245](https://www.openstreetmap.org/node/14202289245), CAC, SITP 382A06 | 4.6928494, -74.1360401 | Named **SITP** bus platform in the old operator's CAC area; historical OPAIN stop 4 name was *CAC*, newer official map calls it *TC2 y 3* |
| 5 — NEAA, Edificio Aeronáutica Civil | [node/6743732547](https://www.openstreetmap.org/node/6743732547), Aeronáutica Civil, SITP 383A06 | 4.690366, -74.1327876 | Named **SITP** platform at the right area, *not* confirmed as shared OPAIN board/alight |
| 6 — Carrera 103, Antigua Zona de Aviación General | [node/5168315104](https://www.openstreetmap.org/node/5168315104), CIAC, SITP 194A05 | 4.6903722, -74.1314057 | Distinct **SITP** platform toward Carrera 103; its OSM name **CIAC** is a location hint only, not the OPAIN stop name |

**Owner decision (2026-11-24): use OPAIN's current official names as the only GTFS stop names.** The OSM names in this table are solely for locating candidate areas, not aliases to publish. The four source-backed **reference points** are recorded under `osm_overpass_export.next_four_stop_candidates` in [source-register.json](../data/opain-public-shuttle/source-register.json). **Owner policy update, 2026-11-24:** it is likely that OPAIN uses the existing SITP stops. Therefore the existing SITP coordinates for **stops 4 (382A06), 5 (383A06), and 6 (194A05)** are adopted as **provisional GTFS stop-coordinate inputs**, while the canonical names remain the current OPAIN names. **Stop 3 (TC1) remains without lat/lon:** a building centroid is not a boarding position, and the nearest OSM public-transport platform is an unlabelled T1-side point around 381 m away. Every `physical_stop_location_reviewed` stays `false`, so adoption is a practical data-model assumption, not independent proof of OPAIN stopping there. The three pre-existing MapVX terminal candidates remain unchanged. No eighth stop is created.

## Grounded official/third-party distinction

- [Current operator schematic](https://storage.eldoradoaero.com/cms/pages/servicios/banners-service-transport/Rutacircular-1.pdf) confirms seven stops and modern aliases **TC2 y 3**, **NEAA** and **Carrera 103** but is NOT a measured geographic map.
- [OPAIN 2020 operating route diagram, annex](https://www.opain.co/archivos/gop-pr-0034-procedimientoserviciobussatliteaeropuerto.pdf), p.13, is more spatially detailed, with stops 3 **TC1**, 4 **CAC**, 5 **NEAA**, 6 **Carrera 103 / Hangar Simón Bolívar** and 7 T2. It is historical and does not resolve the exact 2026 boarding curb; this map explains why stop 4's CAC marker and TC2/3 name refer to the same *logical stop number*, not a second route.
- **Third-party Moovit stop names and service details are considered potentially outdated** and have no authority over the current official OPAIN names, ordering, operating window or headway. Do not use Moovit labels such as `CAC`, `CIAC`, or older T1 door labels as OPAIN GTFS stop names. Historical OPAIN names remain contextual evidence only.
- All three OSM nodes for current OPAIN stops 4–6 are tagged `network=SITP`, not `OPAIN`. They are now **provisionally assigned** to the OPAIN stops because the project owner regards shared boarding locations as likely. A shared OPAIN/SITP kerb is still a hypothesis. The TC1 OSM cargo centroid is inside a building and remains **excluded from the stop coordinates**.

## User-supplied Street View evidence for stop 6 (image dated March 2025)

[Street View location supplied by the owner](https://maps.app.goo.gl/qEp4VNHG1GvYTuNa6?g_st=ac), labelled **Ac. 26 #103-43 a 103-31**, in the Carrera 103 / CISA Entrada 14 area. The screenshot clearly shows an **El Dorado-branded minibus, fleet number 215**, on the Avenida Calle 26 carriageway. The kerb, footpath, fence, a freestanding commercial/information board and the entrance-area signage are visible.

**What this establishes:** strong visual support for the historical El Dorado shuttle using this roadside location in March 2025, consistent with OPAIN stop no. 6 **Carrera 103 – Antigua Zona de Aviación General**.

**What it does not establish:** that the bus is stopped to board passengers, that the small board is an OPAIN Bus Satélite stop pole (it is not legibly identified as such), the exact 2026 curbside stop coordinates, or that the 2025 fleet remains the 2026 vehicle fleet. The provided Google Maps short URL did not expose a machine-verifiable coordinate in this review. **Do not promote the 2025 photo location to verified 2026 `stop_lat`/`stop_lon`.**

Evidence is described and linked in the central register; the Google Street View screenshot is **not** committed or republished.

## User-supplied Street View for stop 5: SITP 383A06 confirmed (March 2025)

The owner supplied [Street View near 10653 Ac. 26](https://maps.app.goo.gl/WrfiDNMAjxPCYgFE6?g_st=ac) showing a clearly legible **bus pole marked 383A06** at the curb, with the ordinary Bogotá city-bus/SITP bus symbol and line information. This **exact reference** matches OSM [node/6743732547](https://www.openstreetmap.org/node/6743732547), named Aeronáutica Civil, network SITP, ref 383A06.

This is strong photographic corroboration that the **SITP** location used as the research-area reference for official **OPAIN stop 5, Edificio Aeronáutica Civil (NEAA)** exists physically. It is **not** a visibly OPAIN-branded Bus Satélite pole and does not prove that the two bus services share the boarding platform. The SITP 383A06 coordinates are now **provisionally used for OPAIN stop 5** by owner policy, not because this photo independently established OPAIN use. OPAIN naming remains authoritative.

## Next narrow action before true GPS stop coordinates

**Prioritize TC1:** find a real roadside bus stop near the first cargo terminal, not the building centroid. Existing T1 (two distinct stops), T2, and SITP-backed 4–6 coordinates now provide six provisional points for a research route test. Validate whether OPAIN actually shares the SITP boarding kerbs at 4–6 as better visual evidence appears; do not block route-model prototyping solely because it has not yet appeared. Once TC1 has a plausible stop on the proper road side, reconstruct the directed circular road shape and estimate segment times using GraphHopper, keeping the 15-vs-20-minute headway conflict explicit.

**Status:** seven OPAIN-named stops in correct order, **six provisional GPS positions** (three MapVX + three SITP), **one unresolved TC1 stop** (only a cargo building centroid available, not suitable for boarding), zero independent OPAIN boarding confirmations at the SITP platforms, no public GTFS and no changes to indoor Pathways.

## New TC1 cargo-access Street View reference (owner, 2026-11-24)

The user supplied a Google Street View screenshot dated **March 2025**; its Google Maps address bar has camera coordinates **4.6939551, -74.1386152**, heading 191.7°. The picture shows **Oficinas de Carga** and a fenced cargo access entrance signed with a large **11** and, immediately below, **TC1** in yellow on the black strip (confirmed by the owner). **This confirms the location is specifically the TC1 cargo entrance**, not merely an unidentified cargo office frontage. This is a better *area/road-access reference* than the previous OSM TC1 building-centroid candidate for further street inspection. The sign **11** marks a cargo access and must not be confused with the distinct T1 passenger-terminal **Puerta 11** public shuttle stop. A dedicated OPAIN boarding pole or boarding activity is **not visible**, and the map URL's coordinates are the Street View camera location, not a stop coordinate. Keep `BOG_OPAIN_SAT_03.lat/lon = null` pending an actual kerb/stop selection.
