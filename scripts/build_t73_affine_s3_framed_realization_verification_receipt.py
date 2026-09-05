#!/usr/bin/env python3
"""Rerun full affine framed-link verification and persist its receipt."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from verify_t73_affine_s3_framed_realization import DATA,verify
ROOT=Path(__file__).resolve().parents[1];VERIFIER=ROOT/"scripts/verify_t73_affine_s3_framed_realization.py";OUTPUT=ROOT/"audit/t73_affine_s3_framed_realization_verification.json"
def fs(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
if __name__=="__main__":
 d=json.loads(DATA.read_text());result=verify()
 if result["verdict"]!="PASS_CANONICAL_AFFINE_S3_FRAMED_LINK_EMBEDDING":raise AssertionError("full affine framed verification failed")
 r={"schema":"t73_affine_s3_framed_realization_verification/v1","affine_framed_realization_sha256":d["sha256"],"verifier_path":str(VERIFIER.relative_to(ROOT)).replace("\\","/"),"verifier_sha256":fs(VERIFIER),"full_verifier_result":result,"verdict":result["verdict"]};r["sha256"]=cs(r);OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))
