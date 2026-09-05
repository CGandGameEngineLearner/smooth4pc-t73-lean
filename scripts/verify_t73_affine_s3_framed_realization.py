#!/usr/bin/env python3
"""Verify the canonical affine core/push cycles and all corridor separations."""
from __future__ import annotations
import hashlib,json,math
from fractions import Fraction
from pathlib import Path
from shapely.geometry import box
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_affine_s3_framed_realization.json";CORE=ROOT/"geometry/t73_affine_s3_core_realization.json";CV=ROOT/"audit/t73_affine_s3_core_realization_verification.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";AR=ROOT/"geometry/t73_actual_ar_link.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def lies(q,a,b):
 d=(b[0]-a[0],b[1]-a[1]);e=(q[0]-a[0],q[1]-a[1]);axis=0 if d[0] else 1 if d[1] else None
 if axis is None:return q==a
 t=e[axis]/d[axis];return 0<=t<=1 and e[0]==t*d[0] and e[1]==t*d[1]
def verify():
 d=json.loads(DATA.read_text());core=json.loads(CORE.read_text());cv=json.loads(CV.read_text());sp=json.loads(SPINE.read_text());dotdata=json.loads(DOTTED.read_text());ar=json.loads(AR.read_text())
 if d["sha256"]!=sha({k:v for k,v in d.items() if k!="sha256"}) or d["affine_s3_core_realization_sha256"]!=core["sha256"] or d["affine_s3_core_verification_sha256"]!=cv["sha256"] or d["johnson_spine_embedding_sha256"]!=sp["sha256"] or d["actual_dotted_s3_passage_cells_sha256"]!=dotdata["sha256"] or d["actual_ar_link_sha256"]!=ar["sha256"]:raise AssertionError("affine framed source/hash changed")
 p=core["projection_denominator"];basis=((Fraction(1),0,Fraction(1,p)),(0,Fraction(1),Fraction(1,p**2)));height=(Fraction(-1,p),Fraction(-1,p**2),Fraction(1));coords=lambda q:(dot(basis[0],q),dot(basis[1],q),dot(height,q))
 core_components={c["component"]:c for c in core["framed_core_components"]};push_components={c["component"]:c for c in d["push_components"]};expected={"m_2":4043,"m_3":19006,"r_xy":20,"r_yz":20,"r_zx":20}
 corridor_paths={};base_core=[];base_push=[]
 for name in expected:
  if d["core_components"][list(expected).index(name)]!=core_components[name]:raise AssertionError("affine core copy changed")
  for source,kind,target in ((core_components[name],"affine_corridor",base_core),(push_components[name],"push_corridor",base_push)):
   vertices=[point(v) for v in source["vertices"]];roles=source["segment_roles"]
   if vertices[0]!=vertices[-1] or len(roles)!=len(vertices)-1 or source["segment_count"]!=expected[name]:raise AssertionError("affine framed cycle closure/count changed")
   for i,(a,b) in enumerate(zip(vertices,vertices[1:])):
    if a==b:raise AssertionError("affine framed cycle has zero segment")
    if roles[i]["kind"]==kind:corridor_paths.setdefault((kind,roles[i]["corridor_index"]),[]).append((a,b))
    else:target.append((a,b))
 if len(corridor_paths)!=7116 or any(len(v)!=4 for v in corridor_paths.values()):raise AssertionError("affine core/push corridor inventory changed")
 core_endpoints=[path[0][0] for key,path in corridor_paths.items() if key[0]=="affine_corridor"]+[path[-1][1] for key,path in corridor_paths.items() if key[0]=="affine_corridor"]
 push_endpoints=[path[0][0] for key,path in corridor_paths.items() if key[0]=="push_corridor"]+[path[-1][1] for key,path in corridor_paths.items() if key[0]=="push_corridor"]
 obstacles=[coords(v)[:2] for v in core_endpoints+push_endpoints]
 if len(obstacles)!=14232 or len(set(obstacles))!=14232:raise AssertionError("affine framed endpoint fibers changed")
 waypoint_checks=0
 for meta in d["push_corridors"]:
  path=corridor_paths[("push_corridor",meta["corridor_index"])];vertices=[path[0][0]]+[x[1] for x in path];values=[coords(v) for v in vertices];h=Fraction(meta["height"]);q=tuple(Fraction(x) for x in meta["projection_waypoint"])
  if h!=-20000-meta["corridor_index"] or not(values[1][:2]==values[0][:2] and values[1][2]==h and values[2][:2]==q and values[2][2]==h and values[3][:2]==values[4][:2] and values[3][2]==h):raise AssertionError("push corridor coordinate rule changed")
  a,b=values[0][:2],values[4][:2]
  for x in obstacles:
   waypoint_checks+=1
   if x not in (a,b) and (lies(x,a,q) or lies(x,q,b)):raise AssertionError("push horizontal route meets endpoint fiber")
 # Broad-phase endpoint-fiber versus every non-corridor base segment.
 base_segments=base_core+base_push;projected=[(coords(a)[:2],coords(b)[:2]) for a,b in base_segments]
 boxes=[box(math.nextafter(float(min(a[0],b[0])),-math.inf),math.nextafter(float(min(a[1],b[1])),-math.inf),math.nextafter(float(max(a[0],b[0])),math.inf),math.nextafter(float(max(a[1],b[1])),math.inf)) for a,b in projected];tree=STRtree(boxes);fiber_candidates=fiber_exact=0
 for q in obstacles:
  qb=box(float(q[0]),float(q[1]),float(q[0]),float(q[1]))
  for raw in tree.query(qb):
   fiber_candidates+=1;a,b=projected[int(raw)]
   if q in (a,b):continue
   fiber_exact+=1
   if lies(q,a,b):raise AssertionError("endpoint projection fiber meets nonincident base segment")
 base_vertices=[v for s in base_segments for v in s]
 if min(coords(v)[2] for v in base_vertices)<=-10000:raise AssertionError("base framed geometry enters corridor height range")
 ribbons=ar["framing"]["spine_ribbon_transport"]["receipts"]
 if not ribbons["pairwise_disjoint_product_ribbons"] or cv["verdict"]!="PASS_CANONICAL_AFFINE_S3_CORE_EMBEDDING":raise AssertionError("base framed geometry evidence missing")
 if (d["core_segment_count"],d["push_segment_count"],d["push_corridor_count"],d["component_count"])!=(23109,23109,3558,12):raise AssertionError("affine framed totals changed")
 return {"verdict":"PASS_CANONICAL_AFFINE_S3_FRAMED_LINK_EMBEDDING","components":12,"core_segments":23109,"push_segments":23109,"push_corridors":3558,"push_waypoint_endpoint_incidence_checks":waypoint_checks,"endpoint_fiber_broad_candidates":fiber_candidates,"endpoint_fiber_exact_nonincident_checks":fiber_exact,"integer_framing_status":"OPEN_PROJECT_COMPLETE_FRAMED_PD"}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
