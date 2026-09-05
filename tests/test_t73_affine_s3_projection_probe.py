from __future__ import annotations
import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_affine_s3_projection_probe.json";SCRIPT=ROOT/"scripts/probe_t73_affine_s3_regular_projection.py";FRAMED=ROOT/"geometry/t73_affine_s3_framed_realization.json"
class AffineProjectionProbeTest(unittest.TestCase):
 def test_probe_receipt(self):
  d=json.loads(DATA.read_text());f=json.loads(FRAMED.read_text());self.assertEqual(d["affine_framed_realization_sha256"],f["sha256"]);self.assertEqual(d["probe_script_sha256"],hashlib.sha256(SCRIPT.read_bytes()).hexdigest().upper());self.assertIsNone(d["selected_linear_projection"]);self.assertGreaterEqual(min(x["broad_candidates"] for x in d["candidates"] if x["result"]=="REGULAR"),250000000);self.assertEqual(d["next_method"],"PIECEWISE_DIAGRAM_ASSEMBLY_FROM_VERIFIED_CHART_PROJECTIONS")
if __name__=="__main__":unittest.main()
