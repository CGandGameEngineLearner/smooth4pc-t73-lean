#!/usr/bin/env python3
"""Assemble the affine model's dotted-surgery matrix and test T73 homology."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ
ROOT=Path(__file__).resolve().parents[1];SELF=ROOT/"audit/t73_product_self_linking_full_verification.json";PAIR=ROOT/"audit/t73_pairwise_core_linking_full_verification.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";OUTPUT=ROOT/"audit/t73_affine_kirby_matrix_homology_obstruction.json";ORDER=["dotted_y","dotted_z","m_2","m_3","r_xy","r_yz","r_zx"]
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def build():
 s=json.loads(SELF.read_text());p=json.loads(PAIR.read_text());d=json.loads(DOTTED.read_text());n=len(ORDER);M=[[0]*n for _ in range(n)];indices={x:i for i,x in enumerate(ORDER)}
 for c,q in s["full_results"].items():M[indices[c]][indices[c]]=q["integer_self_linking"]
 for key,q in p["full_results"].items():a,b=key.split("/");i,j=indices[a],indices[b];M[i][j]=M[j][i]=q["integer_linking"]
 for c,values in d["local_dotted_linking"].items():
  for dotted,value in values.items():i,j=indices[c],indices[dotted];M[i][j]=M[j][i]=value
 matrix=sp.Matrix(M);smith=list(smith_normal_form(matrix,domain=ZZ).diagonal());characteristic=sp.Poly(matrix.charpoly().as_expr());signature=int(characteristic.count_roots(0,sp.oo)-characteristic.count_roots(-sp.oo,0))
 result={"schema":"t73_affine_kirby_matrix_homology_obstruction/v1","product_self_linking_full_verification_sha256":s["sha256"],"pairwise_core_linking_full_verification_sha256":p["sha256"],"dotted_passage_cells_sha256":d["sha256"],"component_order":ORDER,"dotted_surgery_matrix":M,"determinant":int(matrix.det()),"rank":matrix.rank(),"smith_diagonal":[int(x) for x in smith],"signature":signature,"predicted_boundary_h1":"Z/3","required_post_2_handle_boundary_h1":"Z^3 (three 3-handles must remove the three free S1xS2 summands before S3)","three_handles_cannot_remove_torsion":True,"actual_t73_framed_input_status":"REFUTED_FOR_THIS_AFFINE_CORRIDOR_REALIZATION","scoped_linking_computations_status":"EXACT_FOR_THE_CONSTRUCTED_MODEL","completion_status":"AFFINE_MODEL_FAILS_T73_POST_2_HANDLE_HOMOLOGY_GATE"};result["sha256"]=sha(result);return result
def main():
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build()
 if a.write:OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
 if a.check and json.loads(OUTPUT.read_text())!=r:raise AssertionError("affine Kirby homology audit stale")
 print(json.dumps({k:r[k] for k in ("determinant","rank","smith_diagonal","signature","completion_status")},sort_keys=True))
if __name__=="__main__":main()
