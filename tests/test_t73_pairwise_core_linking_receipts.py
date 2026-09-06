from __future__ import annotations
import importlib.util
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1];SCRIPT=ROOT/"scripts/verify_t73_pairwise_core_linking.py";ORDER=("m_2","m_3","r_xy","r_yz","r_zx")
class PairwiseCoreReceiptsTest(unittest.TestCase):
 def test_all_ten_receipts(self):
  sys.path.insert(0,str(ROOT/"scripts"));s=importlib.util.spec_from_file_location("v",SCRIPT);assert s and s.loader;m=importlib.util.module_from_spec(s);s.loader.exec_module(m);values={}
  for i,a in enumerate(ORDER):
   for b in ORDER[i+1:]:
    r,c=m.check_receipt(a,b);self.assertTrue(all(c.values()));values[(a,b)]=r["integer_linking"]
  self.assertEqual(values,{("m_2","m_3"):-730336,("m_2","r_xy"):-40,("m_2","r_yz"):-1,("m_2","r_zx"):-269,("m_3","r_xy"):-189,("m_3","r_yz"):1,("m_3","r_zx"):-1271,("r_xy","r_yz"):0,("r_xy","r_zx"):0,("r_yz","r_zx"):0})
if __name__=="__main__":unittest.main()
