from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_affine_kirby_matrix_homology_audit.py"
class AffineKirbyHomologyAuditTest(unittest.TestCase):
 def test_obstruction(self):
  s=importlib.util.spec_from_file_location("v",SCRIPT);assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.verify();self.assertEqual(r["verdict"],"PASS_AFFINE_KIRBY_MATRIX_HOMOLOGY_OBSTRUCTION");self.assertEqual(r["determinant"],-3);self.assertFalse(r["actual_t73_input"])
if __name__=="__main__":unittest.main()
