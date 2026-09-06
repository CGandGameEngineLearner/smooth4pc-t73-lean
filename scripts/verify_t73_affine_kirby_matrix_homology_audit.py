#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"audit/t73_affine_kirby_matrix_homology_obstruction.json";SELF=ROOT/"audit/t73_product_self_linking_full_verification.json";PAIR=ROOT/"audit/t73_pairwise_core_linking_full_verification.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def verify():
 d=json.loads(DATA.read_text());s=json.loads(SELF.read_text());p=json.loads(PAIR.read_text());M=sp.Matrix(d["dotted_surgery_matrix"])
 if d["sha256"]!=sha({k:v for k,v in d.items() if k!="sha256"}) or d["product_self_linking_full_verification_sha256"]!=s["sha256"] or d["pairwise_core_linking_full_verification_sha256"]!=p["sha256"]:raise AssertionError("homology audit source/hash changed")
 smith=[int(x) for x in smith_normal_form(M,domain=ZZ).diagonal()]
 if M!=M.T or M.det()!=-3 or M.rank()!=7 or smith!=[1,1,1,1,1,1,3] or d["signature"]!=-3:raise AssertionError("affine Kirby matrix algebra changed")
 if not d["three_handles_cannot_remove_torsion"] or d["actual_t73_framed_input_status"]!="REFUTED_FOR_THIS_AFFINE_CORRIDOR_REALIZATION":raise AssertionError("homology obstruction scope changed")
 return {"verdict":"PASS_AFFINE_KIRBY_MATRIX_HOMOLOGY_OBSTRUCTION","determinant":-3,"rank":7,"smith_diagonal":smith,"predicted_boundary_h1":"Z/3","actual_t73_input":False,"repair_status":"OPEN_RECONSTRUCT_RELATIVE_CORRIDOR_FRAMING_AND_LINKING"}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
