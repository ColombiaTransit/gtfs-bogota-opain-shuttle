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

The provisional GraphHopper `bus` profile now generates a complete one-way-aware road shape and estimated leg durations. Before a stable release we must still confirm the boarding positions (especially TC1) and reconcile the conflicting 15/20-minute operating headways.

## GitHub repository visibility

This repository is **public**, so generated GitHub Actions artifacts are accessible according to GitHub's public-repository artifact permissions. **INTERNAL/NOT-FOR-ROUTING is a quality and publication warning, not an access-control guarantee.** The generator and validator run here; no public GitHub Release or stable passenger-facing GTFS URL has been created. Do not place credentials, personal information or proprietary MapVX raw traces in repository or workflow artifacts.

## Release workflow, tags and fixed download filename

[**Release OPAIN public shuttle GTFS (version + latest)**](.github/workflows/release-opain-gtfs.yml) is a **manual** GitHub Actions workflow. It runs seven GraphHopper `bus` road legs, the GTFS generator, all regression/release-gate tests and MobilityData's validator before any version or `latest` tag is updated. **A pull request runs validation only and never publishes.**

The public GitHub Release asset name is always:

```text
gtfs-bogota-opain-shuttle.zip
```

For a version such as `v0.1.0-preview.1`, the intended download addresses after a successful manual publication are:

- Version-pinned: `https://github.com/ColombiaTransit/gtfs-bogota-opain-shuttle/releases/download/v0.1.0-preview.1/gtfs-bogota-opain-shuttle.zip`
- Floating: `https://github.com/ColombiaTransit/gtfs-bogota-opain-shuttle/releases/download/latest/gtfs-bogota-opain-shuttle.zip`

**Tag semantics:** `vMAJOR.MINOR.PATCH` versions and `vMAJOR.MINOR.PATCH-preview.N` preview tags are immutable. Only the `latest` tag is moved when the next validated, explicitly approved release is published. The `latest` GitHub Release has a replaceable fixed-name asset. Previews are marked **prereleases**; GitHub's automatic “Latest” badge may not apply to a prerelease, but the explicit `/releases/download/latest/` URL is still the canonical floating download. A release also attaches an assumptions manifest with the *same fixed basename* and `.manifest.json` suffix.

**Manual invocation:** open **Actions → Release OPAIN public shuttle GTFS (version + latest) → Run workflow**, choose `main`, then select:

| Input | Provisional example | Verified production example |
| --- | --- | --- |
| `version` | `v0.1.0-preview.1` | `v1.0.0` |
| `channel` | `preview` | `stable` |
| `headway_minutes` | `20` (explicit scenario) | selected confirmed interval |
| `confirmation` | `PUBLISH_PROVISIONAL` | `PUBLISH_VERIFIED` |

Preview builds are **publicly downloadable research data**, even though they are marked “NOT FOR ROUTING”; neither operator-verified stops nor observed timetables are guaranteed. Stable builds require all passenger boarding positions, TC1, service headway and source evidence to be confirmed, all generator release blockers resolved, and zero MobilityData warnings or errors. **The current dataset cannot pass the stable gate.** The workflow was added without triggering a release.

Do not use a non-versioned tag like `latest` as the manual version input. Any new official version needs a new version tag; no workflow overwrites an earlier version. The `latest` URL is intended for consumers who explicitly accept that the feed can change.
