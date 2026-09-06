#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FULL=ROOT/"audit/t73_product_self_linking_full_verification.json";FRAMED=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json";CLEAR=ROOT/"audit/t73_affine_s3_product_ribbon_global_clearance.json";OUTPUT=ROOT/"geometry/t73_verified_integer_surgery_framings.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def build():
 f=json.loads(FULL.read_text());fr=json.loads(FRAMED.read_text());cl=json.loads(CLEAR.read_text());values={k:v["integer_self_linking"] for k,v in f["full_results"].items()};r={"schema":"t73_verified_integer_surgery_framings/v1","product_self_linking_full_verification_sha256":f["sha256"],"affine_product_framed_receipt_sha256":fr["sha256"],"product_ribbon_global_clearance_sha256":cl["sha256"],"component_order":["m_2","m_3","r_xy","r_yz","r_zx"],"integer_surgery_framings":values,"definition":"oriented linking number of each affine core with its globally verified product push-off","crossing_signed_sums":{k:v["signed_sum"] for k,v in f["full_results"].items()},"completion_status":"FIVE_AFFINE_PRODUCT_INTEGER_SURGERY_FRAMINGS_VERIFIED","pairwise_core_linking_status":"OPEN","complete_framed_pd_status":"OPEN"};r["sha256"]=sha(r);return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build()
 if a.write:OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
 if a.check and json.loads(OUTPUT.read_text())!=r:raise AssertionError("integer surgery framings stale")
 print(json.dumps(r["integer_surgery_framings"],sort_keys=True))
if __name__=="__main__":main()
