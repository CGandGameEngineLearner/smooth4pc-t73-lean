#!/usr/bin/env python3
"""Independently verify the canonical affine-S3 seven-component core embedding."""
from __future__ import annotations
import hashlib,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_affine_s3_core_realization.json";ATLAS=ROOT/"geometry/t73_complete_framed_dotted_atlas.json";CYCLES=ROOT/"geometry/t73_final_component_passage_cycles.json";PROV=ROOT/"geometry/t73_reduced_source_connector_provenance.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";PROJECTION=ROOT/"audit/t73_actual_source_connector_projection_receipt.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def lies(q,a,b):
 d=(b[0]-a[0],b[1]-a[1]);e=(q[0]-a[0],q[1]-a[1]);axis=0 if d[0] else 1 if d[1] else None
 if axis is None:return q==a
 t=e[axis]/d[axis];return 0<=t<=1 and e[0]==t*d[0] and e[1]==t*d[1]
def verify():
 d=json.loads(DATA.read_text());atlas=json.loads(ATLAS.read_text());cycles=json.loads(CYCLES.read_text());prov=json.loads(PROV.read_text());sp=json.loads(SPINE.read_text());dotdata=json.loads(DOTTED.read_text());projection=json.loads(PROJECTION.read_text())
 if d["sha256"]!=sha({k:v for k,v in d.items() if k!="sha256"}):raise AssertionError("affine core SHA changed")
 bindings={"complete_framed_dotted_atlas_sha256":atlas["sha256"],"final_component_passage_cycles_sha256":cycles["sha256"],"reduced_source_connector_provenance_sha256":prov["sha256"],"johnson_spine_embedding_sha256":sp["sha256"],"actual_dotted_s3_passage_cells_sha256":dotdata["sha256"],"source_connector_projection_receipt_sha256":projection["sha256"]}
 if any(d[k]!=v for k,v in bindings.items()):raise AssertionError("affine core source binding changed")
 p=d["projection_denominator"];basis=((Fraction(1),0,Fraction(1,p)),(0,Fraction(1),Fraction(1,p**2)));height=(Fraction(-1,p),Fraction(-1,p**2),Fraction(1))
 def coords(q):return (dot(basis[0],q),dot(basis[1],q),dot(height,q))
 used_connector_ids=set(sp["components"][1]["connector_ids"]+sp["components"][2]["connector_ids"]);connectors={x["connector_id"]:[point(v) for v in x["polyline"]] for x in sp["central_connectors"] if x["connector_id"] in used_connector_ids};local={x["passage_id"]:[point(v) for v in x["core_vertices"]] for c in dotdata["charts"] for x in c["passages"]}
 endpoint_points=[]
 for x in connectors.values():endpoint_points += [x[0],x[-1]]
 endpoint_points += [v for x in local.values() for v in (x[0],x[-1])];obstacles=[coords(v)[:2] for v in endpoint_points]
 if len(obstacles)!=7116 or len(set(obstacles))!=7116:raise AssertionError("affine endpoint fibers changed")
 corridor_paths={};central_checks=local_checks=zero_checks=0
 expected_segments={"m_2":4043,"m_3":19006,"r_xy":20,"r_yz":20,"r_zx":20}
 for component in d["framed_core_components"]:
  vertices=[point(v) for v in component["vertices"]];roles=component["segment_roles"]
  if vertices[0]!=vertices[-1] or len(roles)!=len(vertices)-1 or component["segment_count"]!=expected_segments[component["component"]]:raise AssertionError("affine component closure/count changed")
  for i,(a,b) in enumerate(zip(vertices,vertices[1:])):
   if a==b:zero_checks+=1
   role=roles[i]
   if role["kind"]=="affine_corridor":corridor_paths.setdefault(role["corridor_index"],[]).append((i,a,b))
   elif role["kind"]=="actual_central_connector":
    central_checks+=1
   else:
    if [a,b] not in [path for path in local.values()] and [b,a] not in [path for path in local.values()]:raise AssertionError("stored local passage segment changed")
    local_checks+=1
 if zero_checks or len(corridor_paths)!=3558 or any(len(v)!=4 for v in corridor_paths.values()):raise AssertionError("corridor segmentation changed")
 waypoint_checks=height_checks=0
 for meta in d["corridors"]:
  path=corridor_paths[meta["corridor_index"]];vertices=[path[0][1]]+[x[2] for x in path];cs=[coords(v) for v in vertices];h=Fraction(meta["height"]);q=tuple(Fraction(x) for x in meta["projection_waypoint"])
  if not (cs[1][:2]==cs[0][:2] and cs[1][2]==h and cs[2][:2]==q and cs[2][2]==h and cs[3][:2]==cs[4][:2] and cs[3][2]==h):raise AssertionError("affine corridor coordinate rule changed")
  if h!=-10000-meta["corridor_index"]:raise AssertionError("corridor height order changed")
  a,b=cs[0][:2],cs[4][:2]
  for x in obstacles:
   waypoint_checks+=1
   if x not in (a,b) and (lies(x,a,q) or lies(x,q,b)):raise AssertionError("corridor horizontal route meets endpoint fiber")
  height_checks+=1
 base_vertices=[v for x in connectors.values() for v in x]+[v for x in local.values() for v in x]
 if min(coords(v)[2] for v in base_vertices)<=-10000:raise AssertionError("corridor horizontal planes do not clear base geometry")
 if projection["verdict"]!="PASS_ACTUAL_SOURCE_CONNECTOR_PROJECTION_FULL_CACHE":raise AssertionError("actual connector embedding receipt missing")
 if (central_checks,local_checks,len(d["corridors"]),d["framed_core_segment_count"])!=(7092,1785,3558,23109):raise AssertionError("affine core inventory changed")
 return {"verdict":"PASS_CANONICAL_AFFINE_S3_CORE_EMBEDDING","components":7,"framed_core_segments":23109,"central_connector_segments":central_checks,"local_hopf_segments":local_checks,"corridors":3558,"corridor_segments":14232,"endpoint_fibers":7116,"waypoint_endpoint_incidence_checks":waypoint_checks,"distinct_corridor_heights":height_checks,"framed_push_status":"OPEN_CONSTRUCT_AFFINE_PUSH_CORRIDORS"}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
