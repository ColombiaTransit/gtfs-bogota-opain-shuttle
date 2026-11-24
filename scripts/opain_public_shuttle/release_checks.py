#!/usr/bin/env python3
"""Strict GTFS release preflight and publishing safeguards (no GitHub API calls)."""
import argparse
import csv
import io
import json
import re
import zipfile
from pathlib import Path

FIXED_NAME = "gtfs-bogota-opain-shuttle.zip"
TAG_RE = re.compile(r"^v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?$")
EXPECTED_FILES = {
    "agency.txt", "calendar.txt", "feed_info.txt", "frequencies.txt",
    "routes.txt", "shapes.txt", "stop_times.txt", "stops.txt", "trips.txt"
}


def verify_inputs(version, channel, confirmation):
    if not TAG_RE.fullmatch(version):
        raise ValueError("Use a version tag such as v0.1.0-preview.1 or v1.0.0 (never latest)")
    if channel not in ("preview", "stable"):
        raise ValueError("Invalid channel")
    is_prerelease = "-" in version
    if channel == "preview" and not is_prerelease:
        raise ValueError("Preview versions must include a prerelease suffix, e.g. v0.1.0-preview.1")
    if channel == "stable" and is_prerelease:
        raise ValueError("Stable versions must be plain vMAJOR.MINOR.PATCH")
    expected = "PUBLISH_PROVISIONAL" if channel == "preview" else "PUBLISH_VERIFIED"
    if confirmation != expected:
        raise ValueError(f"Explicit acknowledgement required: {expected}")
    return True


def _table(zf, name):
    return list(csv.DictReader(io.StringIO(zf.read(name).decode("utf-8-sig"))))


def verify_candidate(zip_path, manifest_path, report_path, source_path, channel):
    if zip_path.name != FIXED_NAME:
        raise ValueError("GTFS release filename must stay gtfs-bogota-opain-shuttle.zip")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    source = json.loads(source_path.read_text(encoding="utf-8"))
    with zipfile.ZipFile(zip_path) as archive:
        if set(archive.namelist()) != EXPECTED_FILES:
            raise ValueError("Missing, unexpected, or duplicate GTFS files; road shape is mandatory")
        stops = _table(archive, "stops.txt")
        trips = _table(archive, "trips.txt")
        shape = _table(archive, "shapes.txt")
        times = _table(archive, "stop_times.txt")
        if len(stops) != 7 or len(times) != 8 or len(shape) <= 8 or len(trips) != 1:
            raise ValueError("Expected seven OPAIN stops, eight circular stop visits and nontrivial road shape")
        official = sorted(source["stops"], key=lambda r: r["sequence"])
        if [r["stop_name"] for r in stops] != [r["name_es"] for r in official]:
            raise ValueError("Release must retain official current OPAIN stop names and order")
        if times[0]["stop_id"] != times[-1]["stop_id"]:
            raise ValueError("Missing return to T1 terminal at end of circular trip")
        if trips[0].get("shape_id") != shape[0].get("shape_id"):
            raise ValueError("GraphHopper shape must be linked to trip")
        if float(times[-1].get("shape_dist_traveled", "0")) <= 0:
            raise ValueError("Missing stop progression along the shape")
    if not manifest.get("modelling_assumptions", {}).get("shape_generated"):
        raise ValueError("A release requires a generated road shape")
    if not manifest.get("modelling_assumptions", {}).get("runtimes_from_graphhopper_osm_bus_not_observed"):
        raise ValueError("A release requires GraphHopper bus road-model times")
    if manifest.get("stop_count") != 7:
        raise ValueError("Unrecognized manifest stop count")
    # MobilityData validator report usually has 'notices' as a list with
    # severity and totalNotices, not notice-by-notice instances.
    notices = report.get("notices")
    if not isinstance(notices, list):
        raise ValueError("MobilityData notices array is missing")
    blocking = [
        (notice.get("code"), notice.get("severity"))
        for notice in notices
        if str(notice.get("severity", "UNKNOWN")).upper() in ("ERROR", "CRITICAL", "FATAL")
    ]
    if blocking:
        raise ValueError(f"MobilityData validator blocking notices: {blocking}")
    # For stable/production, require zero warnings, plus all observed stop
    # positions and a fully verified operator source model.
    if channel == "stable":
        if notices:
            raise ValueError("Stable release requires zero MobilityData notices")
        if manifest.get("not_validated_boarding_stops") is not False:
            raise ValueError("Stable release blocked: boarding stops are still provisional")
        if manifest.get("tc1_camera_reference_used"):
            raise ValueError("Stable release blocked: TC1 still uses Street View camera position")
        if manifest.get("release_blockers"):
            raise ValueError("Stable release blocked: unresolved source and timetable issues")
        if source.get("service", {}).get("frequency_conflict_pending"):
            raise ValueError("Stable release blocked: conflicting OPAIN headway sources")
        if source.get("service", {}).get("frequency_minutes", {}).get("verified_operational_headway") is None:
            raise ValueError("Stable release blocked: headway is unverified")
        for stop in official:
            if stop.get("physical_stop_location_reviewed") is not True:
                raise ValueError(f"Stable release blocked: {stop['id']} boarding position not verified")
            if stop.get("lat") is None or stop.get("lon") is None:
                raise ValueError(f"Stable release blocked: missing physical coordinates for {stop['id']}")
    elif manifest.get("publication_status") != "PRIVATE_RESEARCH_ONLY_NOT_FOR_PASSENGERS":
        raise ValueError("Preview must clearly identify feed as provisional research data")
    return {"stops":len(stops), "shapes":len(shape), "warnings":len(notices)}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    inputs = sub.add_parser("inputs")
    inputs.add_argument("--version", required=True)
    inputs.add_argument("--channel", choices=("preview","stable"), required=True)
    inputs.add_argument("--confirmation", required=True)
    validation = sub.add_parser("validate")
    validation.add_argument("--zip", type=Path, required=True)
    validation.add_argument("--manifest", type=Path, required=True)
    validation.add_argument("--report", type=Path, required=True)
    validation.add_argument("--source", type=Path, required=True)
    validation.add_argument("--channel", choices=("preview","stable"), required=True)
    args = parser.parse_args()
    try:
        if args.command == "inputs":
            verify_inputs(args.version, args.channel, args.confirmation)
            print(f"Release input gate passed for {args.version} ({args.channel})")
        else:
            print("Release candidate gate passed:", verify_candidate(
                args.zip, args.manifest, args.report, args.source, args.channel))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Release gate rejected: {exc}\n")


if __name__ == "__main__":
    main()
