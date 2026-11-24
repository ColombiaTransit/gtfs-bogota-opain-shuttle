#!/usr/bin/env python3
"""Build an explicitly PROVISIONAL, INTERNAL-ONLY OPAIN public Bus Satelite GTFS.

Not a validated passenger timetable: positions, headway and runtimes contain
stated assumptions. No source route polyline, no airside bus, no Pathways.
"""
import argparse
import csv
import io
import json
import math
import zipfile
from datetime import date
from pathlib import Path

DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / "data/opain-public-shuttle/source-register.json"
TC1_REFERENCE = (4.6939551, -74.1386152)  # Street View *camera* at confirmed TC1 access
FILES = (
    "agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt",
    "calendar.txt", "frequencies.txt", "feed_info.txt",
)


def hhmmss(total_seconds):
    if total_seconds < 0:
        raise ValueError("Negative GTFS time")
    return f"{total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}"


def seconds(value):
    parts = [int(x) for x in value.split(":")]
    if len(parts) != 3 or any(x < 0 for x in parts) or parts[1] >= 60 or parts[2] >= 60:
        raise ValueError("Expected HH:MM:SS")
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def haversine_km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    x = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(min(1.0, math.sqrt(x)))


def make_csv(columns, rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def build(source, *, allow_tc1_camera_reference=False, headway_minutes=20,
          mean_speed_kmh=15.0, road_detour_factor=1.4, date_start="20261124",
          date_end="20271231"):
    if headway_minutes not in (15, 20):
        raise ValueError("Research-only headway must be either 15 or 20 minutes")
    if mean_speed_kmh <= 0 or road_detour_factor < 1:
        raise ValueError("Unrealistic leg modelling parameters")
    begin = date.fromisoformat(f"{date_start[:4]}-{date_start[4:6]}-{date_start[6:]}")
    end = date.fromisoformat(f"{date_end[:4]}-{date_end[4:6]}-{date_end[6:]}")
    if begin > end:
        raise ValueError("Invalid calendar range")
    stops = sorted(source["stops"], key=lambda r: r["sequence"])
    if [x["sequence"] for x in stops] != list(range(1, 8)):
        raise ValueError("Official OPAIN circular route must have exactly 7 ordered stops")
    if len({x["id"] for x in stops}) != 7:
        raise ValueError("Duplicate stop IDs")
    if source["stop_naming_policy"]["use_opain_names_for_all_7_stops"] is not True:
        raise ValueError("Do not use non-OPAIN names")
    provisional = []
    coordinates = []
    for stop in stops:
        lat, lon = stop["lat"], stop["lon"]
        if lat is None or lon is None:
            if stop["sequence"] == 3 and allow_tc1_camera_reference:
                lat, lon = TC1_REFERENCE
                kind = "STREET_VIEW_CAMERA_POSITION_NOT_CONFIRMED_BUS_STOP"
            else:
                raise ValueError(f"Missing boarding coordinate for {stop['id']}; use --allow-tc1-camera-reference for internal research ONLY")
        else:
            kind = stop.get("coordinate_status", "PROVISIONAL")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError(f"Invalid coordinate for {stop['id']}")
        provisional.append({"stop_id":stop["id"], "name":stop["name_es"], "source":kind,
                            "lat":lat, "lon":lon,
                            "boarding_confirmed":bool(stop["physical_stop_location_reviewed"])})
        coordinates.append((lat, lon))
    # No shapes.txt: a plausible road geometry must come from GraphHopper/OSM.
    # Distances and segment durations below are explicit straight-line based
    # *modelled* placeholders, not observed or route-planner journey times.
    offsets = [0]
    legs = []
    for idx in range(len(stops)):
        nxt = (idx + 1) % len(stops)
        straight_km = haversine_km(coordinates[idx], coordinates[nxt])
        estimated_seconds = max(60, math.ceil((straight_km * road_detour_factor / mean_speed_kmh * 3600) / 30) * 30)
        # 20-second boarding dwell at each next stop except the loop closure.
        increment = estimated_seconds + (20 if nxt != 0 else 0)
        offsets.append(offsets[-1] + increment)
        legs.append({"from":stops[idx]["id"], "to":stops[nxt]["id"],
                     "straight_line_km":round(straight_km, 4),
                     "estimated_travel_seconds":estimated_seconds,
                     "is_observed":False})
    first_departure = seconds(source["service"]["operating_start_local"])
    service_end = seconds(source["service"]["operating_end_local"])
    if first_departure >= service_end:
        raise ValueError("Invalid official service window")
    # One frequency-based trip pattern; last departure may arrive after midnight.
    trips = [{"route_id":"BOG_OPAIN_PUBLIC_SATELITE","service_id":"OPAIN_DAILY",
              "trip_id":"OPAIN_PUBLIC_CIRCULAR_PROVISIONAL","trip_headsign":"Bus Aeroportuario — Circuito","direction_id":"0"}]
    times = []
    for idx, stop in enumerate(stops + [stops[0]]):
        seconds_since_start = offsets[idx]
        times.append({"trip_id":trips[0]["trip_id"],
                      "arrival_time":hhmmss(first_departure+seconds_since_start),
                      "departure_time":hhmmss(first_departure+seconds_since_start),
                      "stop_id":stop["id"],"stop_sequence":str(idx+1),
                      "pickup_type":"1" if idx==len(stops) else "0",
                      "drop_off_type":"0"})
    rows = {}
    rows["agency.txt"] = make_csv(
        ["agency_id","agency_name","agency_url","agency_timezone","agency_lang"],
        [{"agency_id":"OPAIN","agency_name":"OPAIN — Bus Aeroportuario",
          "agency_url":"https://eldorado.aero/transporte/como-llegar-al-aeropuerto",
          "agency_timezone":"America/Bogota","agency_lang":"es"}])
    rows["stops.txt"] = make_csv(
        ["stop_id","stop_name","stop_lat","stop_lon","location_type"],
        [{"stop_id":s["id"],"stop_name":s["name_es"],
          "stop_lat":f"{c[0]:.7f}","stop_lon":f"{c[1]:.7f}","location_type":"0"}
         for s,c in zip(stops,coordinates)])
    rows["routes.txt"] = make_csv(
        ["route_id","agency_id","route_short_name","route_long_name","route_type","route_url"],
        [{"route_id":"BOG_OPAIN_PUBLIC_SATELITE","agency_id":"OPAIN","route_short_name":"Bus Satélite",
          "route_long_name":"Bus Aeroportuario — T1, carga y T2",
          "route_type":"3","route_url":"https://eldorado.aero/transporte/como-llegar-al-aeropuerto"}])
    rows["trips.txt"] = make_csv(["route_id","service_id","trip_id","trip_headsign","direction_id"],trips)
    rows["stop_times.txt"] = make_csv(
        ["trip_id","arrival_time","departure_time","stop_id","stop_sequence","pickup_type","drop_off_type"],times)
    rows["calendar.txt"] = make_csv(
        ["service_id","monday","tuesday","wednesday","thursday","friday","saturday","sunday","start_date","end_date"],
        [{"service_id":"OPAIN_DAILY",**{day:"1" for day in
          ("monday","tuesday","wednesday","thursday","friday","saturday","sunday")},
          "start_date":date_start,"end_date":date_end}])
    rows["frequencies.txt"] = make_csv(
        ["trip_id","start_time","end_time","headway_secs","exact_times"],
        [{"trip_id":trips[0]["trip_id"],"start_time":hhmmss(first_departure),
          "end_time":hhmmss(service_end),
          "headway_secs":str(headway_minutes*60),"exact_times":"0"}])
    rows["feed_info.txt"] = make_csv(
        ["feed_publisher_name","feed_publisher_url","feed_lang","feed_version","feed_start_date","feed_end_date"],
        [{"feed_publisher_name":"ColombiaTransit — PRIVATE RESEARCH ONLY",
          "feed_publisher_url":"https://github.com/ColombiaTransit/gtfs-bogota-opain-shuttle",
          "feed_lang":"es","feed_version":"OPAIN_INTERNAL_PROVISIONAL_V0",
          "feed_start_date":date_start,"feed_end_date":date_end}])
    assert set(rows)==set(FILES)
    manifest={
        "publication_status":"PRIVATE_RESEARCH_ONLY_NOT_FOR_PASSENGERS",
        "not_operator_issued":True,
        "not_validated_boarding_stops":True,
        "official_stop_sequence_and_names":True,
        "stop_count":len(stops),
        "tc1_camera_reference_used":allow_tc1_camera_reference,
        "tc1_camera_is_not_boarding_pole":True,
        "headway_minutes_ASSUMED_NOT_CONFIRMED":headway_minutes,
        "source_headways_disagree_minutes":[15,20],
        "operating_window_source":"OPAIN operator transport page 04:00–24:00 daily",
        "modelling_assumptions":{
            "average_speed_kmh":mean_speed_kmh,
            "road_detour_factor":road_detour_factor,
            "boarding_dwell_seconds":20,
            "leg_distances_are_straight_line_approximations":True,
            "all_stop_to_stop_durations_are_estimates":True,
            "shape_generated":False,
        },
        "estimated_loop_duration_seconds":offsets[-1],
        "positions":provisional,
        "modelled_legs":legs,
        "release_blockers":[
            "Real TC1 boarding position missing; Street View camera substituted for testing only",
            "OPAIN shared SITP platforms not independently confirmed",
            "T1 Puerta 11 MapVX bus cue assignment unverified",
            "Official 15 vs 20 min headway conflict",
            "No verified street shape, travel times or operating timetable",
            "Run MobilityData validator; passing syntax checks does not establish factual accuracy"
        ]
    }
    return rows, manifest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    parser.add_argument("--output",type=Path,default=Path("inspection-results/opain-public-shuttle/OPAIN-PUBLIC-SHUTTLE-PROVISIONAL-NOT-FOR-ROUTING.zip"))
    parser.add_argument("--allow-tc1-camera-reference",action="store_true")
    parser.add_argument("--headway-minutes",type=int,choices=(15,20),default=20)
    parser.add_argument("--start-date",default="20261124")
    parser.add_argument("--end-date",default="20271231")
    args=parser.parse_args()
    source=json.loads(args.source.read_text(encoding="utf-8"))
    files,manifest=build(source,allow_tc1_camera_reference=args.allow_tc1_camera_reference,
          headway_minutes=args.headway_minutes,date_start=args.start_date,date_end=args.end_date)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in files.items():
            archive.writestr(name,data)
    manifest_file=args.output.with_suffix(".manifest.json")
    manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"PRIVATE research GTFS: {args.output}; stops={manifest['stop_count']}, "
          f"modelled loop={manifest['estimated_loop_duration_seconds']} seconds")
    print(f"Assumptions manifest: {manifest_file}")


if __name__=="__main__":
    main()
