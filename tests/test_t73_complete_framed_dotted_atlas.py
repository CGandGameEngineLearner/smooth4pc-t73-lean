from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_complete_framed_dotted_atlas.py"
class CompleteDottedAtlasTest(unittest.TestCase):
 def test_complete_atlas(self):
  s=importlib.util.spec_from_file_location("v",SCRIPT);assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.verify();self.assertEqual(r["verdict"],"PASS_COMPLETE_SEVEN_COMPONENT_FRAMED_DOTTED_ATLAS");self.assertEqual(r["framed_core_segments"],80007);self.assertEqual(r["single_affine_s3_chart_status"],"OPEN")
if __name__=="__main__":unittest.main()
