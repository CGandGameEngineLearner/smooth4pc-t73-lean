#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_verified_integer_surgery_framings.json";FULL=ROOT/"audit/t73_product_self_linking_full_verification.json";RECEIPTS={c:ROOT/f"audit/t73_product_self_linking_{c.replace('_','')}_receipt.json" for c in ("m_2","m_3","r_xy","r_yz","r_zx")}
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def verify():
 d=json.loads(DATA.read_text());f=json.loads(FULL.read_text());expected={"m_2":-156621,"m_3":-3338112,"r_xy":-1,"r_yz":-1,"r_zx":-3}
 if d["sha256"]!=sha({k:v for k,v in d.items() if k!="sha256"}) or d["product_self_linking_full_verification_sha256"]!=f["sha256"]:raise AssertionError("integer framing hash/source changed")
 if f["verdict"]!="PASS_ALL_FIVE_PRODUCT_SELF_LINKINGS_FULL" or d["integer_surgery_framings"]!=expected:raise AssertionError("integer framing values changed")
 checks=0
 for c,p in RECEIPTS.items():
  r=json.loads(p.read_text());q=f["full_results"][c]
  if f["component_receipt_sha256"][c]!=r["sha256"] or q["crossings"]!=r["crossing_count"] or q["exact_crossings_recomputed"]!=r["crossing_count"] or not q["database_sha_checked"] or 2*expected[c]!=q["signed_sum"]:raise AssertionError("integer framing receipt mismatch")
  checks+=1
 if d["completion_status"]!="FIVE_AFFINE_MODEL_PRODUCT_SELF_LINKINGS_VERIFIED_NOT_T73_INPUT" or d["t73_actual_input_status"]!="REFUTED_BY_DOTTED_SURGERY_HOMOLOGY":raise AssertionError("integer framing scope changed")
 return {"verdict":"PASS_FIVE_AFFINE_MODEL_PRODUCT_SELF_LINKINGS_ONLY","framings":expected,"component_full_receipts":checks,"t73_actual_input":False,"pairwise_core_linking_status":"FULL_MODEL_VALUES_VERIFIED","complete_framed_pd_status":"OPEN"}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
