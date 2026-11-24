#!/usr/bin/env python3
"""Route the seven OPAIN public stops with the private GraphHopper bus profile.

The server URL comes exclusively from GRAPHHOPPER_URL (GitHub org variable).
Outputs source-backed road geometry, distances and bus-profile travel times.
Fail closed on missing segments / teleporting connectors. No raw service URL
is printed, recorded or committed.
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from build_gtfs import TC1_REFERENCE, haversine_km

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def route_url(base):
    base = base.strip().rstrip("/")
    if not base.startswith(("https://", "http://")):
        raise ValueError("GraphHopper server address must use https:// or http://")
    parsed = urllib.parse.urlsplit(base)
    if not parsed.netloc:
        raise ValueError("Invalid GraphHopper server address")
    # Support both GH origin root and explicitly provided /route endpoint.
    return base if parsed.path.rstrip("/").endswith("/route") else base + "/route"


def get_stops(source, allow_tc1_camera_reference):
    stops = sorted(source["stops"], key=lambda s: s["sequence"])
    if [s["sequence"] for s in stops] != list(range(1, 8)):
        raise ValueError("Expected seven official OPAIN stops")
    coordinates = []
    for stop in stops:
        if stop["lat"] is None or stop["lon"] is None:
            if stop["sequence"] != 3 or not allow_tc1_camera_reference:
                raise ValueError("A stop location is missing; TC1 research fallback requires explicit opt-in")
            coordinates.append(TC1_REFERENCE)
        else:
            coordinates.append((stop["lat"], stop["lon"]))
    return stops, coordinates


def send_request(url, points, *, timeout=35, retry=2):
    payload = json.dumps({
        "profile": "bus",
        "points": [[lon, lat] for lat, lon in points],
        "points_encoded": False,
        "instructions": False,
        "calc_points": True,
        "elevation": False
    }).encode("utf-8")
    headers = {"Content-Type":"application/json", "Accept":"application/json", "User-Agent":USER_AGENT}
    if os.getenv("CF_ACCESS_CLIENT_ID") and os.getenv("CF_ACCESS_CLIENT_SECRET"):
        headers["CF-Access-Client-Id"] = os.environ["CF_ACCESS_CLIENT_ID"]
        headers["CF-Access-Client-Secret"] = os.environ["CF_ACCESS_CLIENT_SECRET"]
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    for attempt in range(retry + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                if response.status != 200:
                    raise ValueError("GraphHopper HTTP response was not 200")
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Avoid printing private service URLs, response bodies or tokens.
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry:
                raise RuntimeError(f"GraphHopper route request failed: HTTP {exc.code}") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry:
                raise RuntimeError("GraphHopper route request failed: timeout or network error") from None
        time.sleep(1.2 * (attempt + 1))
    raise RuntimeError("GraphHopper route request did not succeed")


def parse_leg(response, start, end, index):
    paths=response.get("paths") or []
    if len(paths) < 1:
        raise ValueError(f"GraphHopper returned no bus path for leg {index}")
    path=paths[0]
    shape=path.get("points") or {}
    if shape.get("type") != "LineString":
        raise ValueError(f"GraphHopper bus path missing GeoJSON LineString for leg {index}")
    coords=shape.get("coordinates") or []
    if len(coords)<2:
        raise ValueError(f"GraphHopper bus path too short for leg {index}")
    if not all(len(p)>=2 and -180 <= p[0] <=180 and -90 <= p[1] <= 90 for p in coords):
        raise ValueError(f"Invalid GraphHopper geometry in leg {index}")
    distance=float(path.get("distance",0))
    millis=float(path.get("time",0))
    if distance <= 0 or millis <= 0:
        raise ValueError(f"Missing GraphHopper distance/time in leg {index}")
    start_snap=haversine_km(start,(coords[0][1],coords[0][0]))*1000
    end_snap=haversine_km(end,(coords[-1][1],coords[-1][0]))*1000
    # The stop positions are provisional; flag snapping uncertainty and reject
    # very large displacements rather than silently accepting implausible places.
    if max(start_snap,end_snap)>500:
        raise ValueError(f"Bus routing leg {index} stop snaps exceed 500m; inspect curb/side and bus access")
    straight=haversine_km(start,end)*1000
    if distance > max(10000, 25 * straight):
        raise ValueError(f"GraphHopper bus leg {index} has excessive detour; review stop side/direction")
    return {"index":index,"coordinates":[[float(x),float(y)] for x,y,*rest in coords],
        "distance_m":round(distance,2),"travel_seconds":max(1,math.ceil(millis/1000)),
        "first_snap_distance_m":round(start_snap,1),"last_snap_distance_m":round(end_snap,1),
        "flags":["STOP_SNAP_OVER_100M"] if max(start_snap,end_snap)>100 else []}


def compile_routes(stops, coords, responses):
    if len(responses)!=7:
        raise ValueError("Seven directed GraphHopper segments are required")
    legs=[parse_leg(response,coords[i],coords[(i+1)%7],i+1) for i,response in enumerate(responses)]
    full=[]
    cumdist=0.0
    visit_dist=[0.0]
    for i,leg in enumerate(legs):
        vertices=leg["coordinates"]
        if full:
            gap=haversine_km((full[-1][1],full[-1][0]),(vertices[0][1],vertices[0][0]))*1000
            if gap>5:
                raise ValueError(f"Disconnected road geometry at stop {i+1}: gap {gap:.1f}m")
            # Stop-side snaps from consecutive queries must join on the same
            # directed road. Do not add a straight chord between legs.
            vertices=vertices[1:]
        for v in vertices:
            if full:
                cumdist+=haversine_km((full[-1][1],full[-1][0]),(v[1],v[0]))*1000
            full.append(v)
        visit_dist.append(round(cumdist,1))
    if len(full)<8:
        raise ValueError("Incomplete connected circular road geometry")
    return {"schema_version":1,
        "status":"GRAPHOPPER_BUS_ROUTING_RESEARCH_ONLY",
        "profile":"bus",
        "shape_id":"OPAIN_PUBLIC_CIRCULAR_GH_BUS_PROVISIONAL",
        "stops":[{"stop_id":s["id"],"lat":c[0],"lon":c[1]}
                 for s,c in zip(stops,coords)],
        "legs":legs,
        "shape_points_lon_lat":full,
        "stop_visit_shape_dist_m":visit_dist,
        "geometry_length_m":round(cumdist,2),
        "leg_distance_sum_m":round(sum(l["distance_m"] for l in legs),2),
        "travel_seconds_sum":sum(l["travel_seconds"] for l in legs),
        "snap_over_100m_count":sum(bool(l["flags"]) for l in legs),
        "assumed_boarding_positions":True,
        "no_public_release":True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,
        default=Path(__file__).resolve().parents[2]/"data/opain-public-shuttle/source-register.json")
    p.add_argument("--output",type=Path,
        default=Path("inspection-results/opain-public-shuttle/graphhopper-bus-route.json"))
    p.add_argument("--allow-tc1-camera-reference",action="store_true")
    args=p.parse_args()
    gh=os.getenv("GRAPHHOPPER_URL","")
    if not gh:
        raise SystemExit("Missing GitHub organization variable GRAPHHOPPER_URL")
    url=route_url(gh)
    data=json.loads(args.source.read_text(encoding="utf-8"))
    stops, coords=get_stops(data,args.allow_tc1_camera_reference)
    results=[]
    for i in range(7):
        print(f"GraphHopper bus: leg {i+1}/7 {stops[i]['id']} -> {stops[(i+1)%7]['id']}",flush=True)
        results.append(send_request(url,[coords[i],coords[(i+1)%7]]))
    result=compile_routes(stops,coords,results)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    gj={"type":"FeatureCollection","features":[{
        "type":"Feature","properties":{"shape_id":result["shape_id"],"profile":"bus"},
        "geometry":{"type":"LineString","coordinates":result["shape_points_lon_lat"]}
    }]}
    args.output.with_suffix(".geojson").write_text(json.dumps(gj,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"GraphHopper bus: 7/7 directed legs, {len(result['shape_points_lon_lat'])} points, "
          f"{result['geometry_length_m']:.0f}m, {result['travel_seconds_sum']}s moving, "
          f"{result['snap_over_100m_count']} snap warnings",flush=True)


if __name__=="__main__":
    main()
