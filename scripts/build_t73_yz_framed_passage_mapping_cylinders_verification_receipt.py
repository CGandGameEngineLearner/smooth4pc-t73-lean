#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from verify_t73_yz_framed_passage_mapping_cylinders import RECEIPT,verify_full
ROOT=Path(__file__).resolve().parents[1];VERIFIER=ROOT/"scripts/verify_t73_yz_framed_passage_mapping_cylinders.py";OUTPUT=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_verification.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
if __name__=="__main__":
 construction=json.loads(RECEIPT.read_text());result=verify_full(check_cache_sha=True)
 if result["verdict"]!="PASS_ALL_YZ_FRAMED_PASSAGE_MAPPING_CYLINDERS_FULL":raise AssertionError("full yz cylinder verification failed")
 r={"schema":"t73_yz_framed_passage_mapping_cylinders_verification/v1","construction_receipt_sha256":construction["sha256"],"verifier_path":str(VERIFIER.relative_to(ROOT)).replace("\\","/"),"verifier_sha256":sha(VERIFIER),"full_verifier_result":result,"verdict":result["verdict"]};r["sha256"]=csha(r);OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))
