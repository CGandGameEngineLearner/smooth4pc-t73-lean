#!/usr/bin/env python3
"""Build genuine ruled product push-offs along every affine core corridor."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CORE=ROOT/"geometry/t73_affine_s3_core_realization.json";CORE_VERIFY=ROOT/"audit/t73_affine_s3_core_realization_verification.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";AR=ROOT/"geometry/t73_actual_ar_link.json";DEFAULT_OUTPUT=Path.home()/".cache/t73_affine_s3_product_framed_realization.json";RECEIPT=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def enc(v):return [str(x) for x in v]
def add(a,b):return tuple(a[i]+b[i] for i in range(3))
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def scale(t,a):return tuple(t*x for x in a)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def build():
 core=json.loads(CORE.read_text());cv=json.loads(CORE_VERIFY.read_text());sp=json.loads(SPINE.read_text());dotted=json.loads(DOTTED.read_text());ar=json.loads(AR.read_text());w=Fraction(ar["framing"]["spine_ribbon_transport"]["width"]);used=set(sp["components"][1]["connector_ids"]+sp["components"][2]["connector_ids"]);central_ids={x["connector_id"] for x in sp["central_connectors"] if x["connector_id"] in used}
 endpoint_push={}
 for x in sp["central_connectors"]:
  if x["connector_id"] in used:
   q=[point(v) for v in x["polyline"]]
   for v in (q[0],q[-1]):endpoint_push[v]=add(v,(w,w,w))
 for c in dotted["charts"]:
  for p in c["passages"]:
   q=[point(v) for v in p["core_vertices"]];r=[point(v) for v in p["push_vertices"]];endpoint_push[q[0]]=r[0];endpoint_push[q[-1]]=r[-1]
 if len(endpoint_push)!=7116:raise AssertionError("product endpoint map changed")
 push_components=[];ribbons=[];triangle_count=0
 for component in core["framed_core_components"]:
  vertices=[point(v) for v in component["vertices"]];roles=component["segment_roles"];push=[];i=0
  while i<len(roles):
   role=roles[i]
   if role["kind"]=="affine_corridor":
    index=role["corridor_index"];path=vertices[i:i+5]
    if any(roles[i+j]["kind"]!="affine_corridor" or roles[i+j]["corridor_index"]!=index for j in range(4)):raise AssertionError("core corridor block changed")
    n0=sub(endpoint_push[path[0]],path[0]);n1=sub(endpoint_push[path[-1]],path[-1]);normals=[add(scale(1-Fraction(j,4),n0),scale(Fraction(j,4),n1)) for j in range(5)];pushed=[add(v,n) for v,n in zip(path,normals)]
    triangles=[]
    for j in range(4):
     triangles.extend(((j,j+1,5+j+1),(j,5+j+1,5+j)))
     tangent=sub(path[j+1],path[j])
     if cross(tangent,normals[j])==(0,0,0) or cross(tangent,normals[j+1])==(0,0,0):raise AssertionError(f"corridor {index} product ribbon degenerates")
    ribbons.append({"corridor_index":index,"component":component["component"],"core_vertex_range":[i,i+4],"endpoint_normal_start":enc(n0),"endpoint_normal_end":enc(n1),"normal_field":[enc(v) for v in normals],"push_vertices":[enc(v) for v in pushed],"ribbon_triangles":[list(v) for v in triangles],"triangle_count":8});triangle_count+=8
    if not push:push.extend(pushed)
    else:
     if push[-1]!=pushed[0]:raise AssertionError("product corridor push does not meet previous block")
     push.extend(pushed[1:])
    i+=4;continue
   a,b=vertices[i],vertices[i+1]
   if role["kind"]=="actual_central_connector":pa,pb=add(a,(w,w,w)),add(b,(w,w,w))
   elif role["kind"]=="dotted_passage":pa,pb=endpoint_push[a],endpoint_push[b]
   else:raise AssertionError("unknown affine core segment role")
   if not push:push.append(pa)
   elif push[-1]!=pa:raise AssertionError("product push block incidence failed")
   push.append(pb);i+=1
  if len(push)!=len(vertices) or push[0]!=push[-1]:raise AssertionError("product push component did not close")
  push_components.append({"component":component["component"],"vertices":[enc(v) for v in push],"segment_count":len(push)-1,"closed":True})
 r={"schema":"t73_affine_s3_product_framed_realization/v1","affine_s3_core_realization_sha256":core["sha256"],"affine_s3_core_verification_sha256":cv["sha256"],"johnson_spine_embedding_sha256":sp["sha256"],"actual_dotted_s3_passage_cells_sha256":dotted["sha256"],"actual_ar_link_sha256":ar["sha256"],"core_components":core["framed_core_components"],"dotted_components":core["dotted_components"],"push_components":push_components,"corridor_product_ribbons":ribbons,"core_segment_count":core["framed_core_segment_count"],"push_segment_count":sum(x["segment_count"] for x in push_components),"corridor_count":len(ribbons),"corridor_ribbon_triangle_count":triangle_count,"component_count":12,"completion_status":"AFFINE_S3_PRODUCT_PUSH_CYCLES_AND_CORRIDOR_RIBBONS_CONSTRUCTED","global_ribbon_embedding_status":"OPEN_EXACT_NONLOCAL_CLEARANCE","integer_framing_status":"OPEN"};r["sha256"]=sha(r);return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path);p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build();output=a.output or DEFAULT_OUTPUT
 if a.write:
  output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n");receipt={"schema":"t73_affine_s3_product_framed_realization_receipt/v1","cache_path":str(output),"cache_size":output.stat().st_size,"cache_sha256":file_sha(output),"payload_sha256":r["sha256"],"builder_sha256":file_sha(Path(__file__)),"affine_s3_core_realization_sha256":r["affine_s3_core_realization_sha256"],"corridor_count":r["corridor_count"],"corridor_ribbon_triangle_count":r["corridor_ribbon_triangle_count"],"core_segment_count":r["core_segment_count"],"push_segment_count":r["push_segment_count"],"global_ribbon_embedding_status":r["global_ribbon_embedding_status"],"verdict":"PASS_AFFINE_PRODUCT_RIBBON_LOCAL_CONSTRUCTION_ONLY"};receipt["sha256"]=sha(receipt);RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 if a.check and json.loads(output.read_text())!=r:raise AssertionError("product framed affine realization stale")
 print(json.dumps({"status":r["completion_status"],"corridors":r["corridor_count"],"triangles":r["corridor_ribbon_triangle_count"],"push":r["push_segment_count"]},sort_keys=True))
if __name__=="__main__":main()
