#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os
from pathlib import Path
from verify_t73_affine_s3_product_ribbon_clearance import RECEIPT,verify
ROOT=Path(__file__).resolve().parents[1];VERIFIER=ROOT/"scripts/verify_t73_affine_s3_product_ribbon_clearance.py";OUTPUT=ROOT/"audit/t73_affine_s3_product_ribbon_global_clearance.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
if __name__=="__main__":
 construction=json.loads(RECEIPT.read_text());old=os.environ.get("T73_CLEARANCE_PHASE")
 os.environ["T73_CLEARANCE_PHASE"]="triangles";triangle=verify();os.environ["T73_CLEARANCE_PHASE"]="segments";segment=verify()
 if old is None:os.environ.pop("T73_CLEARANCE_PHASE",None)
 else:os.environ["T73_CLEARANCE_PHASE"]=old
 if triangle["verdict"]!="PASS_AFFINE_S3_PRODUCT_RIBBON_TRIANGLE_CLEARANCE_ONLY" or segment["verdict"]!="PASS_AFFINE_S3_PRODUCT_RIBBON_SEGMENT_CLEARANCE_ONLY":raise AssertionError("product ribbon clearance phase failed")
 r={"schema":"t73_affine_s3_product_ribbon_global_clearance/v1","product_framed_payload_sha256":construction["payload_sha256"],"construction_receipt_sha256":construction["sha256"],"verifier_path":str(VERIFIER.relative_to(ROOT)).replace("\\","/"),"verifier_sha256":sha(VERIFIER),"triangle_result":triangle,"segment_result":segment,"verdict":"PASS_AFFINE_S3_PRODUCT_CORRIDOR_RIBBON_GLOBAL_CLEARANCE","embedded_corridor_product_ribbons":True};r["sha256"]=csha(r);OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(r,sort_keys=True))
