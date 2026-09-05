#!/usr/bin/env python3
"""Add five affine product-push cycles to the verified affine S3 core."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
from build_t73_affine_s3_core_realization import ambient,append_path,coords,point,waypoint
ROOT=Path(__file__).resolve().parents[1];CORE=ROOT/"geometry/t73_affine_s3_core_realization.json";CORE_VERIFY=ROOT/"audit/t73_affine_s3_core_realization_verification.json";CYCLES=ROOT/"geometry/t73_final_component_passage_cycles.json";PROV=ROOT/"geometry/t73_reduced_source_connector_provenance.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";AR=ROOT/"geometry/t73_actual_ar_link.json";OUTPUT=ROOT/"geometry/t73_affine_s3_framed_realization.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def enc(v):return [str(x) for x in v]
def add(a,b):return tuple(a[i]+b[i] for i in range(3))
def push_corridor(a,b,index,obstacles):
 ca,cb=coords(a),coords(b);q,attempt=waypoint(ca[:2],cb[:2],obstacles,index+4000);h=Fraction(-20000-index);v=[a,ambient(ca[0],ca[1],h),ambient(q[0],q[1],h),ambient(cb[0],cb[1],h),b];return v,{"corridor_index":index,"height":str(h),"projection_waypoint":[str(x) for x in q],"waypoint_attempt":attempt,"segment_count":4}
def build():
 core=json.loads(CORE.read_text());cv=json.loads(CORE_VERIFY.read_text());cycles=json.loads(CYCLES.read_text());prov=json.loads(PROV.read_text());sp=json.loads(SPINE.read_text());dotted=json.loads(DOTTED.read_text());ar=json.loads(AR.read_text());width=Fraction(ar["framing"]["spine_ribbon_transport"]["width"]);used=set(sp["components"][1]["connector_ids"]+sp["components"][2]["connector_ids"]);connectors={x["connector_id"]:[add(point(v),(width,width,width)) for v in x["polyline"]] for x in sp["central_connectors"] if x["connector_id"] in used};after={(g["component"],e["source_from"]):e["raw_connector_cells"][0]["raw_cell_id"] for g in prov["components"] if g["component"] in ("m_2","m_3") for e in g["reduced_edges"]};local={p["passage_id"]:[point(v) for v in p["push_vertices"]] for c in dotted["charts"] for p in c["passages"]}
 core_endpoints=[]
 for c in core["framed_core_components"]:
  v=[point(x) for x in c["vertices"]]
  for i,r in enumerate(c["segment_roles"]):
   if r["kind"] in ("actual_central_connector","dotted_passage"):
    if i==0 or c["segment_roles"][i-1]!=r:pass
 for q in [x for x in sp["central_connectors"] if x["connector_id"] in used]:core_endpoints += [point(q["polyline"][0]),point(q["polyline"][-1])]
 core_endpoints += [point(v) for c in dotted["charts"] for p in c["passages"] for v in (p["core_vertices"][0],p["core_vertices"][-1])]
 push_endpoints=[v for q in connectors.values() for v in (q[0],q[-1])]+[v for q in local.values() for v in (q[0],q[-1])];obstacles=[coords(v)[:2] for v in core_endpoints+push_endpoints]
 if len(obstacles)!=14232 or len(set(obstacles))!=14232:raise AssertionError("framed endpoint fibers not unique")
 components=[];corridors=[];index=0
 for cycle in cycles["components"]:
  name=cycle["component"];passages=cycle["passages"];vertices=[];roles=[]
  if name in ("m_2","m_3"):
   ids=[after[(name,p["passage_id"])] for p in passages];append_path(vertices,local[passages[0]["passage_id"]]);roles=[{"kind":"local_hopf_push","passage_id":passages[0]["passage_id"]}]
   for i,p in enumerate(passages):
    q,m=push_corridor(vertices[-1],connectors[ids[i]][0],index,obstacles);append_path(vertices,q);roles += [{"kind":"push_corridor","corridor_index":index}]*4;m.update({"component":name,"kind":"passage_to_connector_push"});corridors.append(m);index+=1
    append_path(vertices,connectors[ids[i]]);roles += [{"kind":"actual_central_product_push","connector_id":ids[i]}]*4
    nxt=(i+1)%len(passages);q,m=push_corridor(vertices[-1],local[passages[nxt]["passage_id"]][0],index,obstacles);append_path(vertices,q);roles += [{"kind":"push_corridor","corridor_index":index}]*4;m.update({"component":name,"kind":"connector_to_passage_push"});corridors.append(m);index+=1
    if nxt:append_path(vertices,local[passages[nxt]["passage_id"]]);roles += ([{"kind":"local_hopf_push","passage_id":passages[nxt]["passage_id"]}] if nxt else [])
  else:
   append_path(vertices,local[passages[0]["passage_id"]]);roles=[{"kind":"local_hopf_push","passage_id":passages[0]["passage_id"]}]
   for i,p in enumerate(passages):
    nxt=(i+1)%len(passages);q,m=push_corridor(vertices[-1],local[passages[nxt]["passage_id"]][0],index,obstacles);append_path(vertices,q);roles += [{"kind":"push_corridor","corridor_index":index}]*4;m.update({"component":name,"kind":"dual_passage_push_connector"});corridors.append(m);index+=1
    if nxt:append_path(vertices,local[passages[nxt]["passage_id"]]);roles += ([{"kind":"local_hopf_push","passage_id":passages[nxt]["passage_id"]}] if nxt else [])
  if vertices[0]!=vertices[-1] or len(roles)!=len(vertices)-1:raise AssertionError("affine push cycle did not close")
  components.append({"component":name,"vertices":[enc(v) for v in vertices],"segment_roles":roles,"segment_count":len(roles),"closed":True})
 r={"schema":"t73_affine_s3_framed_realization/v1","affine_s3_core_realization_sha256":core["sha256"],"affine_s3_core_verification_sha256":cv["sha256"],"final_component_passage_cycles_sha256":cycles["sha256"],"reduced_source_connector_provenance_sha256":prov["sha256"],"johnson_spine_embedding_sha256":sp["sha256"],"actual_dotted_s3_passage_cells_sha256":dotted["sha256"],"actual_ar_link_sha256":ar["sha256"],"core_components":core["framed_core_components"],"dotted_components":core["dotted_components"],"push_components":components,"push_corridors":corridors,"component_count":12,"core_segment_count":core["framed_core_segment_count"],"push_segment_count":sum(x["segment_count"] for x in components),"push_corridor_count":len(corridors),"push_corridor_segment_count":4*len(corridors),"completion_status":"CANONICAL_AFFINE_S3_CORE_AND_PUSH_CYCLES_CONSTRUCTED","framed_embedding_verification_status":"OPEN_EXACT_CORE_PUSH_DISJOINTNESS","integer_framing_status":"OPEN"};r["sha256"]=sha(r);return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build()
 if a.write:OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
 if a.check and json.loads(OUTPUT.read_text())!=r:raise AssertionError("affine framed realization stale")
 print(json.dumps({"status":r["completion_status"],"core":r["core_segment_count"],"push":r["push_segment_count"],"corridors":r["push_corridor_count"]},sort_keys=True))
if __name__=="__main__":main()
