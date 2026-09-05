from __future__ import annotations
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_affine_push_corridor_framing_gap.json"
class AffinePushFramingGapTest(unittest.TestCase):
 def test_fail_closed(self):
  d=json.loads(DATA.read_text());self.assertEqual(d["corridor_ribbon_triangle_count"],0);self.assertTrue(d["disjoint_companion_cycles_verified"]);self.assertFalse(d["product_framing_transport_verified"]);self.assertFalse(d["integer_framing_usable"])
if __name__=="__main__":unittest.main()
