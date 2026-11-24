#!/usr/bin/env python3
"""Offline release gates: no GitHub credentials or GraphHopper calls needed."""
import csv
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts/opain_public_shuttle"))
import build_gtfs
import release_checks


class ReleaseWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/"data/opain-public-shuttle/source-register.json").read_text())

    def test_immutable_semver_and_explicit_publish_confirmation(self):
        self.assertTrue(release_checks.verify_inputs(
            "v0.1.0-preview.1", "preview", "PUBLISH_PROVISIONAL"))
        self.assertTrue(release_checks.verify_inputs(
            "v1.0.0", "stable", "PUBLISH_VERIFIED"))
        for args in [
            ("latest", "preview", "PUBLISH_PROVISIONAL"),
            ("v0.1.0", "preview", "PUBLISH_PROVISIONAL"),
            ("v0.1.0-preview.1", "stable", "PUBLISH_VERIFIED"),
            ("v0.1.0-preview.1", "preview", "sure"),
            ("v01.1.0", "stable", "PUBLISH_VERIFIED"),
        ]:
            with self.subTest(inputs=args), self.assertRaises(ValueError):
                release_checks.verify_inputs(*args)

    def make_fixture(self, root):
        files,manifest=build_gtfs.build(self.source,allow_tc1_camera_reference=True)
        # The static no-GraphHopper unit fixture is synthetic; add deterministic
        # dummy road coordinates and markers solely to test release gating.
        stops=list(csv.DictReader(io.StringIO(files["stops.txt"].decode())))
        coords=[[float(r["stop_lon"]),float(r["stop_lat"])] for r in stops]
        coords.append(coords[0])
        shape=build_gtfs.make_csv(
            ["shape_id","shape_pt_lat","shape_pt_lon","shape_pt_sequence","shape_dist_traveled"],
            [{"shape_id":"fixture","shape_pt_lat":str(c[1]),"shape_pt_lon":str(c[0]),
              "shape_pt_sequence":str(i+1),"shape_dist_traveled":str(i*100)}
             for i,c in enumerate([v for pt in zip(coords[:-1],coords[1:]) for v in pt])])
        files["shapes.txt"]=shape
        files["trips.txt"]=files["trips.txt"].decode().replace(
            "direction_id\n","direction_id,shape_id\n").replace(",0\n",",0,fixture\n").encode()
        times=list(csv.DictReader(io.StringIO(files["stop_times.txt"].decode())))
        for i,r in enumerate(times): r["shape_dist_traveled"]=str(i*100)
        files["stop_times.txt"]=build_gtfs.make_csv([
            "trip_id","arrival_time","departure_time","stop_id","stop_sequence",
            "pickup_type","drop_off_type","shape_dist_traveled"],times)
        manifest["modelling_assumptions"]["shape_generated"]=True
        manifest["modelling_assumptions"]["runtimes_from_graphhopper_osm_bus_not_observed"]=True
        out=Path(root)
        z=out/release_checks.FIXED_NAME
        with zipfile.ZipFile(z,"w") as archive:
            for name,data in files.items(): archive.writestr(name,data)
        m=out/"manifest.json"
        m.write_text(json.dumps(manifest))
        r=out/"report.json"
        r.write_text(json.dumps({"notices":[]}))
        src=out/"source.json"
        src.write_text(json.dumps(self.source))
        return z,m,r,src

    def test_provisional_preview_allowed_with_warnings_explained(self):
        with tempfile.TemporaryDirectory() as folder:
            args=self.make_fixture(folder)
            result=release_checks.verify_candidate(*args,"preview")
            self.assertEqual(result["stops"],7)
            self.assertGreater(result["shapes"],8)
            self.assertEqual(result["warnings"],0)

    def test_stable_blocks_unverified_boarding_points(self):
        with tempfile.TemporaryDirectory() as folder:
            args=self.make_fixture(folder)
            with self.assertRaisesRegex(ValueError,"boarding stops"):
                release_checks.verify_candidate(*args,"stable")

    def test_any_mobilitydata_error_blocks_release(self):
        with tempfile.TemporaryDirectory() as folder:
            z,m,r,src=self.make_fixture(folder)
            r.write_text(json.dumps({"notices":[{"code":"invalid_stop_location","severity":"ERROR","totalNotices":1}]}))
            with self.assertRaisesRegex(ValueError,"blocking notices"):
                release_checks.verify_candidate(z,m,r,src,"preview")

    def test_fixed_name_is_mandatory(self):
        with tempfile.TemporaryDirectory() as folder:
            z,m,r,src=self.make_fixture(folder)
            renamed=Path(folder)/"opain-random.zip"
            z.rename(renamed)
            with self.assertRaisesRegex(ValueError,"filename"):
                release_checks.verify_candidate(renamed,m,r,src,"preview")


if __name__=="__main__":
    unittest.main()
