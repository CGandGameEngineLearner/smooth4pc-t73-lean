from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_yz_dotted_passage_replacement_map.py"
class YZDottedReplacementMapTest(unittest.TestCase):
 def test_all_passages(self):
  spec=importlib.util.spec_from_file_location("verify_yz",SCRIPT);assert spec and spec.loader;module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);r=module.verify()
  self.assertEqual(r["verdict"],"PASS_ALL_YZ_PASSAGES_BOUND_TO_DOTTED_S3_REPLACEMENTS");self.assertEqual(r["replacements"],1785);self.assertEqual(r["post_conversion_core_segments"],80007)
if __name__=="__main__":unittest.main()
