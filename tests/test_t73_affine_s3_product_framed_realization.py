from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_affine_s3_product_framed_realization.py"
class ProductFramedLocalTest(unittest.TestCase):
 def test_local_ribbons(self):
  s=importlib.util.spec_from_file_location("v",SCRIPT);assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.verify();self.assertEqual(r["verdict"],"PASS_AFFINE_S3_CORRIDOR_PRODUCT_RIBBONS_LOCAL");self.assertEqual(r["ribbon_triangles"],28464);self.assertEqual(r["global_ribbon_embedding_status"],"OPEN_EXACT_NONLOCAL_CLEARANCE")
if __name__=="__main__":unittest.main()
