from __future__ import annotations
import importlib.util
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_product_self_linking_component.py"
class ProductSelfLinkingReceiptsTest(unittest.TestCase):
 def test_all_five_receipts(self):
  sys.path.insert(0,str(ROOT/"scripts"));s=importlib.util.spec_from_file_location("v",SCRIPT);assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);values={}
  for c in ("m_2","m_3","r_xy","r_yz","r_zx"):
   r,ch=m.check_receipt(c);self.assertTrue(all(ch.values()));values[c]=r["integer_self_linking"]
  self.assertEqual(values,{"m_2":-156621,"m_3":-3338112,"r_xy":-1,"r_yz":-1,"r_zx":-3})
if __name__=="__main__":unittest.main()
