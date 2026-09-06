#!/usr/bin/env python3
"""Rerun all ten exact pairwise ledgers and persist a compact receipt."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from verify_t73_pairwise_core_linking import ORDER,rp,verify_database
ROOT=Path(__file__).resolve().parents[1];VERIFIER=ROOT/"scripts/verify_t73_pairwise_core_linking.py";OUTPUT=ROOT/"audit/t73_pairwise_core_linking_full_verification.json"
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
if __name__=="__main__":
 results={};receipts={}
 for i,a in enumerate(ORDER):
  for b in ORDER[i+1:]:
   q=verify_database(a,b,full=True,check_database_sha=True);r=json.loads(rp(a,b).read_text());key=f"{a}/{b}";receipts[key]=r["sha256"];results[key]={k:q[k] for k in ("crossings","signed_sum","integer_linking","exact_crossings_recomputed","database_sha_checked")}
 out={"schema":"t73_pairwise_core_linking_full_verification/v1","verifier_path":str(VERIFIER.relative_to(ROOT)).replace("\\","/"),"verifier_sha256":hashlib.sha256(VERIFIER.read_bytes()).hexdigest().upper(),"pair_receipt_sha256":receipts,"full_results":results,"total_crossings":sum(x["crossings"] for x in results.values()),"verdict":"PASS_ALL_TEN_PAIRWISE_CORE_LINKINGS_FULL"};out["sha256"]=cs(out);OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,sort_keys=True))
