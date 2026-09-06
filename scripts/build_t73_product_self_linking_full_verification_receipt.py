#!/usr/bin/env python3
"""Rerun all five full self-linking verifiers and persist a compact receipt."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from verify_t73_product_self_linking_component import receipt_path,verify_database
ROOT=Path(__file__).resolve().parents[1];VERIFIER=ROOT/"scripts/verify_t73_product_self_linking_component.py";OUTPUT=ROOT/"audit/t73_product_self_linking_full_verification.json";COMPONENTS=("m_2","m_3","r_xy","r_yz","r_zx")
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
if __name__=="__main__":
 results={};receipts={}
 for c in COMPONENTS:
  q=verify_database(c,full=True,check_database_sha=True);r=json.loads(receipt_path(c).read_text());receipts[c]=r["sha256"];results[c]={k:q[k] for k in ("crossings","signed_sum","integer_self_linking","exact_crossings_recomputed","database_sha_checked")}
 out={"schema":"t73_product_self_linking_full_verification/v1","verifier_path":str(VERIFIER.relative_to(ROOT)).replace("\\","/"),"verifier_sha256":hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),"component_receipt_sha256":receipts,"full_results":results,"verdict":"PASS_ALL_FIVE_PRODUCT_SELF_LINKINGS_FULL"};out["sha256"]=cs(out);OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,sort_keys=True))
