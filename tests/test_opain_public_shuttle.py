#!/usr/bin/env python3
import csv
import importlib.util
import io
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("opain_gtfs", ROOT/"scripts/opain_public_shuttle/build_gtfs.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class PublicOpainShuttleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/"data/opain-public-shuttle/source-register.json").read_text(encoding="utf-8"))

    @staticmethod
    def table(files, name):
        return list(csv.DictReader(io.StringIO(files[name].decode("utf-8"))))

    def test_requires_explicit_tc1_provisional_opt_in(self):
        with self.assertRaisesRegex(ValueError,"Missing boarding coordinate"):
            mod.build(self.source)

    def test_authority_seven_stops_and_no_shapes(self):
        files, manifest=mod.build(self.source,allow_tc1_camera_reference=True)
        self.assertEqual(set(files),set(mod.FILES))
        names=[x["stop_name"] for x in self.table(files,"stops.txt")]
        self.assertEqual(names,[x["name_es"] for x in sorted(self.source["stops"],key=lambda x:x["sequence"])])
        self.assertEqual(len(names),7)
        self.assertNotIn("shapes.txt",files)
        self.assertFalse(manifest["modelling_assumptions"]["shape_generated"])
        self.assertTrue(manifest["tc1_camera_is_not_boarding_pole"])

    def test_tc1_reference_is_camera_not_false_pole(self):
        files,manifest=mod.build(self.source,allow_tc1_camera_reference=True)
        tc1=self.table(files,"stops.txt")[2]
        self.assertEqual((float(tc1["stop_lat"]),float(tc1["stop_lon"])),mod.TC1_REFERENCE)
        self.assertFalse(manifest["positions"][2]["boarding_confirmed"])
        self.assertEqual(manifest["positions"][2]["source"],
                         "STREET_VIEW_CAMERA_POSITION_NOT_CONFIRMED_BUS_STOP")
        self.assertTrue(manifest["not_operator_issued"])

    def test_frequency_and_service_window(self):
        files,manifest=mod.build(self.source,allow_tc1_camera_reference=True)
        freq=self.table(files,"frequencies.txt")[0]
        self.assertEqual(freq["start_time"],"04:00:00")
        self.assertEqual(freq["end_time"],"24:00:00")
        self.assertEqual(freq["headway_secs"],"1200")
        self.assertEqual(freq["exact_times"],"0")
        self.assertEqual(manifest["source_headways_disagree_minutes"],[15,20])
        calendar=self.table(files,"calendar.txt")[0]
        self.assertTrue(all(calendar[x]=="1" for x in
                            ("monday","tuesday","wednesday","thursday","friday","saturday","sunday")))

    def test_round_trip_and_positive_offsets(self):
        files,_=mod.build(self.source,allow_tc1_camera_reference=True)
        st=self.table(files,"stop_times.txt")
        self.assertEqual(len(st),8)
        self.assertEqual(st[0]["stop_id"],st[-1]["stop_id"])
        self.assertEqual(st[-1]["pickup_type"],"1")
        self.assertEqual([int(x["stop_sequence"]) for x in st],list(range(1,9)))
        times=[mod.seconds(x["departure_time"]) for x in st]
        self.assertTrue(all(b>a for a,b in zip(times,times[1:])))

    def test_dates_headway_and_bogus_sequence_rejected(self):
        with self.assertRaises(ValueError):
            mod.build(self.source,allow_tc1_camera_reference=True,headway_minutes=12)
        with self.assertRaises(ValueError):
            mod.build(self.source,allow_tc1_camera_reference=True,date_start="20271231",date_end="20261124")
        modified=json.loads(json.dumps(self.source))
        modified["stops"][1]["sequence"]=1
        with self.assertRaisesRegex(ValueError,"exactly 7"):
            mod.build(modified,allow_tc1_camera_reference=True)

    def test_15_minute_whatif_not_claimed_actual(self):
        files,manifest=mod.build(self.source,allow_tc1_camera_reference=True,headway_minutes=15)
        self.assertEqual(self.table(files,"frequencies.txt")[0]["headway_secs"],"900")
        self.assertTrue(manifest["not_validated_boarding_stops"])
        self.assertEqual(manifest["headway_minutes_ASSUMED_NOT_CONFIRMED"],15)


if __name__=="__main__":
    unittest.main()
