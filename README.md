# OPAIN Bus Satélite — Bogotá El Dorado

Independent GTFS research and generator for the **public/landside** free OPAIN Bus Aeroportuario connecting El Dorado Terminal 1 (two separate stops), cargo terminals, Aeronáutica Civil, Carrera 103, and Terminal 2.

**STATUS: PROVISIONAL TEST DATA — NOT A PASSENGER TIMETABLE OR PUBLIC GTFS RELEASE.** Seven official OPAIN stop names are modeled; six coordinates are sourced provisionally from MapVX/OSM SITP, while the TC1 position is substituted from a *Street View camera location* only when explicitly enabled for testing. Frequencies and leg travel times are still hypotheses.

- [Generator, local instructions and caveats](scripts/opain_public_shuttle/README.md)
- [Central evidence and stop source register](data/opain-public-shuttle/source-register.json)
- [Operator sources and stop list](docs/step-63-opain-public-shuttle-baseline.md)
- [OSM/Overpass comparison](docs/step-64-opain-public-shuttle-osm-comparison.md)
- [Street View and four cargo-side stop candidates](docs/step-65-opain-public-shuttle-four-osm-candidates.md)
- [Private GTFS build and MobilityData validator workflow](.github/workflows/build-opain-public-shuttle-private.yml)

This repository is the **sole active home** for the public OPAIN shuttle and its road-shape research. The separate [Eldorado-mapa](https://github.com/ColombiaTransit/Eldorado-mapa) repository remains responsible for the airport map and indoor GTFS Pathways. The airside shuttle and flights feed are outside this project's scope.

Source data attribution: OPAIN airport transport pages; MapVX source POI evidence collected in the original project; OSM © OpenStreetMap contributors (ODbL). No original MapVX geometry or copyrighted Street View screenshots are redistributed here. The user-provided OSM airport-wide Overpass export was analyzed in the prior project; this repo includes its derived reference IDs/coordinates and findings, **not a copy of the complete original raw export**.

Next priority: build an OSM road routing graph from a reproducible Overpass extraction or GraphHopper, connect all seven provisional stops in the operator's one-way loop order, and validate shape direction and travel times. Never bridge disconnected roads by straight lines and label the result as an actual driveable bus shape.

## GitHub repository visibility

This repository is **public**, so generated GitHub Actions artifacts are accessible according to GitHub's public-repository artifact permissions. **INTERNAL/NOT-FOR-ROUTING is a quality and publication warning, not an access-control guarantee.** The generator and validator run here; no public GitHub Release or stable passenger-facing GTFS URL has been created. Do not place credentials, personal information or proprietary MapVX raw traces in repository or workflow artifacts.
