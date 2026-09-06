from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_verified_integer_surgery_framings.py"
class IntegerFramingsTest(unittest.TestCase):
 def test_five_full_framings(self):
  s=importlib.util.spec_from_file_location("v",SCRIPT);assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.verify();self.assertEqual(r["verdict"],"PASS_FIVE_AFFINE_MODEL_PRODUCT_SELF_LINKINGS_ONLY");self.assertEqual(r["framings"],{"m_2":-156621,"m_3":-3338112,"r_xy":-1,"r_yz":-1,"r_zx":-3});self.assertFalse(r["t73_actual_input"])
if __name__=="__main__":unittest.main()
