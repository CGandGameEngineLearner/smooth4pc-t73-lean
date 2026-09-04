import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_t73_c_h1_relative_isotopy.py"
COEND = ROOT / "scripts" / "build_t73_c_h1_coend_certificate.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CH1RelativeIsotopyGateTest(unittest.TestCase):
    def test_current_source_and_target_counts_match_but_split_matching_fails(self):
        verifier = load(VERIFY, "c_h1_relative_verifier")
        report = verifier.generate_report()
        self.assertEqual(report["status"], "IMPOSSIBLE_LITERAL_SPLIT_BOUNDARY_MATCHING")
        self.assertTrue(report["target_normal_form_present"])
        self.assertTrue(report["target_only_is_not_source_isotopy"])
        self.assertEqual(len(report["missing"]), 2)
        self.assertIsNone(report["boundary_endpoint_mismatch"])
        self.assertEqual(
            sorted(
                report["selected_target"][
                    "endpoint_counts_per_insertion_ball"
                ].values()
            ),
            [88, 88, 542, 542],
        )
        self.assertEqual(
            report["selected_target"]["total_boundary_endpoint_count"], 1260
        )
        obstruction = report["split_matching_obstruction"]
        self.assertEqual(obstruction["active_y_incident_interval_count"], 176)
        self.assertEqual(obstruction["wrong_side_connector_count"], 8)
        self.assertFalse(
            obstruction["literal_two_disjoint_closures_relative_four_balls_possible"]
        )
        self.assertEqual(
            obstruction["transition_counts"],
            {
                "Y_minus--Z_minus": 4,
                "Y_minus--Z_plus": 84,
                "Y_plus--Z_minus": 84,
                "Y_plus--Z_plus": 4,
            },
        )

    def test_legacy_hash_frames_are_rejected(self):
        verifier = load(VERIFY, "c_h1_relative_verifier_legacy")
        legacy = verifier.generate_report()["legacy_product_isotopy"]
        self.assertEqual(legacy["status_field"], "PASS")
        self.assertTrue(legacy["exhibited_product_isotopy_field"])
        self.assertTrue(legacy["rectangle_frames_are_hashes_only"])
        self.assertFalse(legacy["accepted_as_coordinate_movie"])

    def test_default_command_fails_closed(self):
        result = subprocess.run(
            [sys.executable, str(VERIFY)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('"status": "IMPOSSIBLE_LITERAL_SPLIT_BOUNDARY_MATCHING"', result.stdout)

    def test_coend_certificate_cannot_be_built(self):
        builder = load(COEND, "c_h1_coend_builder")
        with self.assertRaisesRegex(RuntimeError, "PASS_COORDINATE_MOVIE"):
            builder.build()

    def test_status_literals_without_coordinates_are_rejected(self):
        verifier = load(VERIFY, "c_h1_relative_verifier_literal")
        fake = {
            "schema": "t73_c_h1_relative_isotopy/v1",
            "status": "PASS",
            "exhibited_product_isotopy": True,
        }
        with self.assertRaises((AssertionError, KeyError)):
            verifier.validate(fake)

    def test_saved_split_obstruction_is_a_hard_validate_failure(self):
        verifier = load(VERIFY, "c_h1_relative_verifier_obstruction")
        source = json.loads(verifier.SOURCE.read_text(encoding="utf-8"))
        target = json.loads(verifier.TARGET.read_text(encoding="utf-8"))
        primitives = json.loads(verifier.PRIMITIVES.read_text(encoding="utf-8"))
        fake = {
            "schema": "t73_c_h1_relative_isotopy/v1",
            "dependencies": {
                "source_exterior_sha256": source["sha256"],
                "selected_canopolis_target_sha256": target["sha256"],
                "all_owner_primitives_sha256": primitives["sha256"],
            },
        }
        with self.assertRaisesRegex(AssertionError, "8 wrong-side connectors"):
            verifier.validate(fake)

    def test_nonedge_source_path_is_rejected(self):
        verifier = load(VERIFY, "c_h1_relative_verifier_edge")
        positions = {
            "a": (verifier.Fraction(0), verifier.Fraction(0), verifier.Fraction(0)),
            "b": (verifier.Fraction(1), verifier.Fraction(0), verifier.Fraction(0)),
            "c": (verifier.Fraction(0), verifier.Fraction(1), verifier.Fraction(0)),
        }
        with self.assertRaisesRegex(AssertionError, "non-edge"):
            verifier.validate_edge_path(
                ["a", "c"], positions, {("a", "b")}, "mutant source strand"
            )

    def test_endpoint_matching_must_equal_saved_incidence(self):
        verifier = load(VERIFY, "c_h1_relative_verifier_endpoints")
        source = json.loads(verifier.SOURCE.read_text(encoding="utf-8"))
        positions = {}
        boundaries = {name: set() for name in verifier.BALL_NAMES}
        records = []
        for sphere in source["insertion_spheres"]:
            for endpoint in sphere["endpoints"]:
                vertex = "vertex:" + endpoint["endpoint_id"]
                positions[vertex] = verifier.qpoint(endpoint["point"])
                boundaries[sphere["name"]].add(vertex)
                records.append(
                    {
                        "ball": sphere["name"],
                        "endpoint_id": endpoint["endpoint_id"],
                        "ambient_vertex": vertex,
                        "orientation": 1,
                    }
                )
        self.assertEqual(
            len(verifier.validate_endpoint_matching(records, source, positions, boundaries)),
            1260,
        )
        records[1]["endpoint_id"] = records[0]["endpoint_id"]
        with self.assertRaisesRegex(AssertionError, "exact saved"):
            verifier.validate_endpoint_matching(records, source, positions, boundaries)

    def test_target_binding_must_be_a_bijection(self):
        verifier = load(VERIFY, "c_h1_relative_verifier_target_bijection")
        source = json.loads(verifier.SOURCE.read_text(encoding="utf-8"))
        target = json.loads(verifier.TARGET.read_text(encoding="utf-8"))
        strand_ids = {
            item["interval_id"] for item in source["exterior_intervals"]
        }
        target_keys = [
            (side, item["index"])
            for side, rows in (
                ("left", target["left_closure_strands"]),
                ("right", target["right_closure_strands"]),
            )
            for item in rows
        ]
        bindings = [
            {
                "source_strand_id": strand_id,
                "target_side": key[0],
                "target_index": key[1],
            }
            for strand_id, key in zip(sorted(strand_ids), target_keys)
        ]
        verifier.target_binding_records(bindings, target, strand_ids)
        bindings[1]["target_side"] = bindings[0]["target_side"]
        bindings[1]["target_index"] = bindings[0]["target_index"]
        with self.assertRaisesRegex(AssertionError, "not bijective on all 630 target"):
            verifier.target_binding_records(bindings, target, strand_ids)


if __name__ == "__main__":
    unittest.main()
