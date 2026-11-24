#!/usr/bin/env python3
"""Offline GraphHopper fixture tests; never require the live private service."""
import csv
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts/opain_public_shuttle"))
import build_gtfs as gtfs
import graphhopper_bus_shape as gh


class GraphHopperOpainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/"data/opain-public-shuttle/source-register.json").read_text())
        cls.stops,cls.coords=gh.get_stops(cls.source,True)

    def responses(self):
        result=[]
        for i in range(7):
            a=self.coords[i]
            b=self.coords[(i+1)%7]
            # Synthetic fixture only: never treat these as real road shapes.
            result.append({"paths":[{"points":{"type":"LineString","coordinates":[
                [a[1],a[0]],[b[1],b[0]]]},"distance":max(100,1000*gtfs.haversine_km(a,b)),
                "time":120000}]})
        return result

    def test_private_route_url_format(self):
        self.assertEqual(gh.route_url("https://graph.example"),"https://graph.example/route")
        self.assertEqual(gh.route_url("https://graph.example/route"),"https://graph.example/route")
        with self.assertRaises(ValueError):
            gh.route_url("localhost:8989")

    def test_requires_explicit_tc1_reference(self):
        with self.assertRaises(ValueError):
            gh.get_stops(self.source,False)

    def test_seven_directed_legs_and_complete_shape(self):
        routing=gh.compile_routes(self.stops,self.coords,self.responses())
        self.assertEqual(len(routing["legs"]),7)
        self.assertEqual(len(routing["stop_visit_shape_dist_m"]),8)
        self.assertEqual(routing["profile"],"bus")
        self.assertTrue(routing["no_public_release"])
        files,manifest=gtfs.build(self.source,allow_tc1_camera_reference=True,graphhopper_route=routing)
        self.assertIn("shapes.txt",files)
        self.assertTrue(manifest["modelling_assumptions"]["shape_generated"])
        trip=list(csv.DictReader(io.StringIO(files["trips.txt"].decode())))[0]
        self.assertEqual(trip["shape_id"],routing["shape_id"])
        stop_times=list(csv.DictReader(io.StringIO(files["stop_times.txt"].decode())))
        self.assertEqual(len(stop_times),8)
        self.assertEqual(float(stop_times[-1]["shape_dist_traveled"]),routing["stop_visit_shape_dist_m"][-1])

    def test_rejects_missing_leg(self):
        with self.assertRaisesRegex(ValueError,"Seven directed"):
            gh.compile_routes(self.stops,self.coords,self.responses()[:-1])

    def test_rejects_huge_off_road_snap(self):
        bad=self.responses()
        bad[0]["paths"][0]["points"]["coordinates"][0]=[-74.0,5.0]
        with self.assertRaisesRegex(ValueError,"500m"):
            gh.compile_routes(self.stops,self.coords,bad)

    def test_rejects_wrong_bus_profile_and_order(self):
        routing=gh.compile_routes(self.stops,self.coords,self.responses())
        routing["profile"]="car"
        with self.assertRaisesRegex(ValueError,"bus-profile"):
            gtfs.build(self.source,allow_tc1_camera_reference=True,graphhopper_route=routing)
        routing["profile"]="bus"
        routing["stops"].reverse()
        with self.assertRaisesRegex(ValueError,"order"):
            gtfs.build(self.source,allow_tc1_camera_reference=True,graphhopper_route=routing)


if __name__=="__main__":
    unittest.main()
