#!/usr/bin/env python3
"""Realize the verified seven-component core atlas in one affine Q3 chart."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
from build_t73_x_m1_ejected_band_lanes import invert
ROOT=Path(__file__).resolve().parents[1];ATLAS=ROOT/"geometry/t73_complete_framed_dotted_atlas.json";CYCLES=ROOT/"geometry/t73_final_component_passage_cycles.json";PROV=ROOT/"geometry/t73_reduced_source_connector_provenance.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";PROJECTION_RECEIPT=ROOT/"audit/t73_actual_source_connector_projection_receipt.json";OUTPUT=ROOT/"geometry/t73_affine_s3_core_realization.json"
P=1000003
BASIS=((Fraction(1),0,Fraction(1,P)),(0,Fraction(1),Fraction(1,P**2)));HEIGHT=(Fraction(-1,P),Fraction(-1,P**2),Fraction(1))
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def enc(v):return [str(x) for x in v]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
M=[list(BASIS[0]),list(BASIS[1]),list(HEIGHT)];INV=invert(M)
def coords(q):return (dot(BASIS[0],q),dot(BASIS[1],q),dot(HEIGHT,q))
def ambient(u,v,w):return tuple(sum(INV[i][j]*x for j,x in enumerate((u,v,w))) for i in range(3))
def lies(q,a,b):
 d=(b[0]-a[0],b[1]-a[1]);e=(q[0]-a[0],q[1]-a[1]);axis=0 if d[0] else 1 if d[1] else None
 if axis is None:return q==a
 t=e[axis]/d[axis];return 0<=t<=1 and e[0]==t*d[0] and e[1]==t*d[1]
def waypoint(a,b,obstacles,index):
 for attempt in range(10000):
  q=(Fraction(20+2*index),Fraction(10000+index)+Fraction(attempt,10001))
  if not any(x not in (a,b) and (lies(x,a,q) or lies(x,q,b)) for x in obstacles):return q,attempt
 raise AssertionError("no projected corridor waypoint")
def corridor(a,b,index,obstacles):
 ca,cb=coords(a),coords(b);q,attempt=waypoint(ca[:2],cb[:2],obstacles,index);h=Fraction(-10000-index)
 vertices=[a,ambient(ca[0],ca[1],h),ambient(q[0],q[1],h),ambient(cb[0],cb[1],h),b]
 return vertices,{"corridor_index":index,"height":str(h),"projection_waypoint":[str(x) for x in q],"waypoint_attempt":attempt,"vertex_count":5,"segment_count":4}
def append_path(vertices,path):
 if vertices and vertices[-1]!=path[0]:raise AssertionError("affine core path incidence failed")
 vertices.extend(path if not vertices else path[1:])
def build():
 projection_receipt=json.loads(PROJECTION_RECEIPT.read_text())
 atlas=json.loads(ATLAS.read_text());cycles=json.loads(CYCLES.read_text());prov=json.loads(PROV.read_text());sp=json.loads(SPINE.read_text());dotted=json.loads(DOTTED.read_text());connectors={x["connector_id"]:[point(v) for v in x["polyline"]] for x in sp["central_connectors"]};after={(g["component"],e["source_from"]):e["raw_connector_cells"][0]["raw_cell_id"] for g in prov["components"] if g["component"] in ("m_2","m_3") for e in g["reduced_edges"]};local={p["passage_id"]:[point(v) for v in p["core_vertices"]] for c in dotted["charts"] for p in c["passages"]}
 endpoint_points=[]
 for name in ("m_2","m_3"):
  for c in [after[(name,p["passage_id"])] for p in next(x for x in cycles["components"] if x["component"]==name)["passages"]]:endpoint_points += [connectors[c][0],connectors[c][-1]]
 endpoint_points += [v for path in local.values() for v in (path[0],path[-1])];obstacles=[coords(v)[:2] for v in endpoint_points]
 if len(obstacles)!=7116 or len(set(obstacles))!=7116:raise AssertionError("affine corridor endpoint projections are not unique")
 components=[];corridors=[];corridor_index=0
 for cycle in cycles["components"]:
  name=cycle["component"];passages=cycle["passages"];vertices=[];roles=[]
  if name in ("m_2","m_3"):
   ids=[after[(name,p["passage_id"])] for p in passages]
   append_path(vertices,local[passages[0]["passage_id"]]);roles += [{"kind":"dotted_passage","passage_id":passages[0]["passage_id"]}]
   for i,p in enumerate(passages):
    exit_path,meta=corridor(vertices[-1],connectors[ids[i]][0],corridor_index,obstacles);append_path(vertices,exit_path);roles += [{"kind":"affine_corridor","corridor_index":corridor_index}]*4;meta.update({"component":name,"kind":"passage_to_connector","passage_id":p["passage_id"]});corridors.append(meta);corridor_index+=1
    append_path(vertices,connectors[ids[i]]);roles += [{"kind":"actual_central_connector","connector_id":ids[i]}]*4
    nxt=(i+1)%len(passages);entry_path,meta=corridor(vertices[-1],local[passages[nxt]["passage_id"]][0],corridor_index,obstacles);append_path(vertices,entry_path);roles += [{"kind":"affine_corridor","corridor_index":corridor_index}]*4;meta.update({"component":name,"kind":"connector_to_passage","passage_id":passages[nxt]["passage_id"]});corridors.append(meta);corridor_index+=1
    if nxt:append_path(vertices,local[passages[nxt]["passage_id"]]);roles += ([{"kind":"dotted_passage","passage_id":passages[nxt]["passage_id"]}] if nxt else [])
  else:
   append_path(vertices,local[passages[0]["passage_id"]]);roles=[{"kind":"dotted_passage","passage_id":passages[0]["passage_id"]}]
   for i,p in enumerate(passages):
    nxt=(i+1)%len(passages);path,meta=corridor(vertices[-1],local[passages[nxt]["passage_id"]][0],corridor_index,obstacles);append_path(vertices,path);roles += [{"kind":"affine_corridor","corridor_index":corridor_index}]*4;meta.update({"component":name,"kind":"dual_passage_connector","passage_id":p["passage_id"]});corridors.append(meta);corridor_index+=1
    if nxt:append_path(vertices,local[passages[nxt]["passage_id"]]);roles += ([{"kind":"dotted_passage","passage_id":passages[nxt]["passage_id"]}] if nxt else [])
  if vertices[0]!=vertices[-1] or len(roles)!=len(vertices)-1:raise AssertionError("affine component did not close")
  components.append({"component":name,"vertices":[enc(v) for v in vertices],"segment_roles":roles,"segment_count":len(roles),"closed":True})
 charts={c["dotted_component"]:[point(v) for v in c["dotted_vertices"]] for c in dotted["charts"]}
 result={"schema":"t73_affine_s3_core_realization/v1","complete_framed_dotted_atlas_sha256":atlas["sha256"],"final_component_passage_cycles_sha256":cycles["sha256"],"reduced_source_connector_provenance_sha256":prov["sha256"],"johnson_spine_embedding_sha256":sp["sha256"],"actual_dotted_s3_passage_cells_sha256":dotted["sha256"],"source_connector_projection_receipt_sha256":projection_receipt["sha256"],"projection_denominator":P,"projection_basis":[[str(x) for x in row] for row in BASIS],"height_direction":[str(x) for x in HEIGHT],"dotted_components":[{"component":k,"vertices":[enc(v) for v in q],"segment_count":4} for k,q in charts.items()],"framed_core_components":components,"corridors":corridors,"corridor_count":len(corridors),"corridor_segment_count":4*len(corridors),"framed_core_segment_count":sum(c["segment_count"] for c in components),"component_count":7,"completion_status":"CANONICAL_AFFINE_S3_CORE_REALIZATION_CONSTRUCTED","embedding_verification_status":"OPEN_EXACT_ALL_SEGMENT_DISJOINTNESS"};result["sha256"]=sha(result);return result
def main():
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build()
 if a.write:OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
 if a.check and json.loads(OUTPUT.read_text())!=r:raise AssertionError("affine S3 core stale")
 print(json.dumps({"status":r["completion_status"],"corridors":r["corridor_count"],"segments":r["framed_core_segment_count"]},sort_keys=True))
if __name__=="__main__":main()
