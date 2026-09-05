from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_yz_framed_passage_mapping_cylinders.py"
class YZCylinderReceiptTest(unittest.TestCase):
 def test_receipt(self):
  spec=importlib.util.spec_from_file_location("verify_yzc",SCRIPT);assert spec and spec.loader;m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r,c=m.check_receipt();self.assertTrue(all(c.values()));self.assertEqual(r["mapping_cylinder_tetrahedron_count"],21408)
if __name__=="__main__":unittest.main()
