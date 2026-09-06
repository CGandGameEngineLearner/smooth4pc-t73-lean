#!/usr/bin/env python3
"""Verify local product fields and ruled ribbons of the affine push cycles."""
from __future__ import annotations
import hashlib,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RECEIPT=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json";CORE=ROOT/"geometry/t73_affine_s3_core_realization.json";CV=ROOT/"audit/t73_affine_s3_core_realization_verification.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";AR=ROOT/"geometry/t73_actual_ar_link.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def add(a,b):return tuple(a[i]+b[i] for i in range(3))
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def scale(t,a):return tuple(t*x for x in a)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def verify():
 receipt=json.loads(RECEIPT.read_text());d=json.loads(resolve(receipt["cache_path"]).read_text());core=json.loads(CORE.read_text());cv=json.loads(CV.read_text());sp=json.loads(SPINE.read_text());dot=json.loads(DOTTED.read_text());ar=json.loads(AR.read_text())
 if receipt["payload_sha256"]!=d["sha256"]:raise AssertionError("product framed receipt payload changed")
 if d["sha256"]!=sha({k:v for k,v in d.items() if k!="sha256"}) or d["affine_s3_core_realization_sha256"]!=core["sha256"] or d["affine_s3_core_verification_sha256"]!=cv["sha256"] or d["johnson_spine_embedding_sha256"]!=sp["sha256"] or d["actual_dotted_s3_passage_cells_sha256"]!=dot["sha256"] or d["actual_ar_link_sha256"]!=ar["sha256"]:raise AssertionError("product framed source/hash changed")
 core_components={c["component"]:c for c in core["framed_core_components"]};push_components={c["component"]:c for c in d["push_components"]};ribbons={r["corridor_index"]:r for r in d["corridor_product_ribbons"]}
 if len(ribbons)!=3558:raise AssertionError("corridor ribbon inventory changed")
 triangle_checks=normal_checks=endpoint_checks=0
 for name,c in core_components.items():
  cvx=[point(v) for v in c["vertices"]];pvx=[point(v) for v in push_components[name]["vertices"]]
  if len(cvx)!=len(pvx) or pvx[0]!=pvx[-1]:raise AssertionError("product push cycle changed")
  i=0
  while i<len(c["segment_roles"]):
   role=c["segment_roles"][i]
   if role["kind"]!="affine_corridor":i+=1;continue
   idx=role["corridor_index"]
   if any(c["segment_roles"][i+j].get("corridor_index")!=idx for j in range(4)):raise AssertionError("core corridor subdivision changed")
   path=cvx[i:i+5];pushed=pvx[i:i+5];r=ribbons[idx];n0=point(r["endpoint_normal_start"]);n1=point(r["endpoint_normal_end"]);raw=[add(scale(1-Fraction(j,4),n0),scale(Fraction(j,4),n1)) for j in range(5)];normals=[raw[0]]+[scale(Fraction(1,1000),v) for v in raw[1:4]]+[raw[4]]
   if [point(v) for v in r["normal_field"]]!=normals or [point(v) for v in r["push_vertices"]]!=pushed:raise AssertionError("corridor product field changed")
   if sub(pushed[0],path[0])!=n0 or sub(pushed[-1],path[-1])!=n1:raise AssertionError("corridor product endpoints changed")
   endpoint_checks+=2
   for j in range(4):
    tangent=sub(path[j+1],path[j])
    for normal in (normals[j],normals[j+1]):
     normal_checks+=1
     if not any(normal) or cross(tangent,normal)==(0,0,0):raise AssertionError("corridor normal vanishes or is tangent")
   vertices=path+pushed
   for ids in r["ribbon_triangles"]:
    a,b,e=[vertices[k] for k in ids];triangle_checks+=1
    if cross(sub(b,a),sub(e,a))==(0,0,0):raise AssertionError("corridor ribbon triangle degenerated")
   i+=4
 if (d["core_segment_count"],d["push_segment_count"],d["corridor_ribbon_triangle_count"],triangle_checks,normal_checks,endpoint_checks)!=(23109,23109,28464,28464,28464,7116):raise AssertionError("product framed totals changed")
 if d["completion_status"]!="AFFINE_S3_PRODUCT_PUSH_CYCLES_AND_CORRIDOR_RIBBONS_CONSTRUCTED" or d["global_ribbon_embedding_status"]!="OPEN_EXACT_NONLOCAL_CLEARANCE" or d["corridor_interior_normal_shrink"]!="1/1000":raise AssertionError("product framed scope changed")
 return {"verdict":"PASS_AFFINE_S3_CORRIDOR_PRODUCT_RIBBONS_LOCAL","core_segments":23109,"push_segments":23109,"corridors":3558,"ribbon_triangles":triangle_checks,"normal_transversality_checks":normal_checks,"endpoint_product_normal_matches":endpoint_checks,"global_ribbon_embedding_status":d["global_ribbon_embedding_status"]}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
