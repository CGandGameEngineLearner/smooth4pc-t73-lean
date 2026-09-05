#!/usr/bin/env python3
"""Exact global clearance of all affine corridor product ribbons."""
from __future__ import annotations
import json,math,os,sys
from fractions import Fraction
from pathlib import Path
from shapely.geometry import box,LineString,Polygon
from shapely.strtree import STRtree
from verify_t73_candidate_t_band0_splice import exact_segment_intersection
ROOT=Path(__file__).resolve().parents[1];RECEIPT=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json";CORE=ROOT/"geometry/t73_affine_s3_core_realization.json"
P=1000003;HEIGHT=(Fraction(-1,P),Fraction(-1,P**2),Fraction(1))
def point(v):return tuple(Fraction(x) for x in v)
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def bbox(values):
 low=[min(v[i] for v in values) for i in range(3)];high=[max(v[i] for v in values) for i in range(3)]
 heights=[sum(float(HEIGHT[i])*float(v[i]) for i in range(3)) for v in values]
 return low,high,box(math.nextafter(float(low[0]),-math.inf),math.nextafter(float(low[1]),-math.inf),math.nextafter(float(high[0]),math.inf),math.nextafter(float(high[1]),math.inf)),math.nextafter(min(heights),-math.inf),math.nextafter(max(heights),math.inf)
def projected_geometry(values):
 q=[(float(v[0]),float(v[1])) for v in values]
 geometry=Polygon(q) if len(q)==3 else LineString(q)
 if geometry.is_empty or not geometry.is_valid:geometry=LineString(q)
 return geometry.buffer(1e-8)
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def det3(a,b,c):return dot(a,cross(b,c))
def point_in_triangle_2d(p,t):
 def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 values=[orient(t[i],t[(i+1)%3],p) for i in range(3)]
 return all(x>=0 for x in values) or all(x<=0 for x in values)
def project2(v,drop):return tuple(v[i] for i in range(3) if i!=drop)
def segment_triangle(segment,triangle):
 p,q=segment;a,b,c=triangle;direction=sub(q,p);u=sub(b,a);v=sub(c,a);rhs=sub(a,p);den=det3(direction,tuple(-x for x in u),tuple(-x for x in v))
 if den:
  t=det3(rhs,tuple(-x for x in u),tuple(-x for x in v))/den;alpha=det3(direction,rhs,tuple(-x for x in v))/den;beta=det3(direction,tuple(-x for x in u),rhs)/den
  return 0<=t<=1 and alpha>=0 and beta>=0 and alpha+beta<=1
 normal=cross(u,v)
 if dot(normal,sub(p,a)) or dot(normal,sub(q,a)):return False
 drop=max(range(3),key=lambda i:abs(normal[i]));s=(project2(p,drop),project2(q,drop));t2=tuple(project2(x,drop) for x in triangle)
 return point_in_triangle_2d(s[0],t2) or point_in_triangle_2d(s[1],t2) or any(exact_segment_intersection(s,(t2[i],t2[(i+1)%3])) for i in range(3))
def triangles_intersect(first,second):
 return any(segment_triangle((first[i],first[(i+1)%3]),second) for i in range(3)) or any(segment_triangle((second[i],second[(i+1)%3]),first) for i in range(3))
def projected_triangles_intersect(first,second):
 a=tuple((v[0],v[1]) for v in first);b=tuple((v[0],v[1]) for v in second)
 if any(exact_segment_intersection((a[i],a[(i+1)%3]),(b[j],b[(j+1)%3])) for i in range(3) for j in range(3)):return True
 def area(t):return (t[1][0]-t[0][0])*(t[2][1]-t[0][1])-(t[1][1]-t[0][1])*(t[2][0]-t[0][0])
 return (area(a)!=0 and point_in_triangle_2d(b[0],a)) or (area(b)!=0 and point_in_triangle_2d(a[0],b))
def projected_segment_triangle_intersect(segment,triangle):
 s=tuple((v[0],v[1]) for v in segment);t=tuple((v[0],v[1]) for v in triangle)
 area=(t[1][0]-t[0][0])*(t[2][1]-t[0][1])-(t[1][1]-t[0][1])*(t[2][0]-t[0][0])
 return (area!=0 and (point_in_triangle_2d(s[0],t) or point_in_triangle_2d(s[1],t))) or any(exact_segment_intersection(s,(t[i],t[(i+1)%3])) for i in range(3))
def verify():
 receipt=json.loads(RECEIPT.read_text());d=json.loads(resolve(receipt["cache_path"]).read_text());triangles=[]
 core_by={c["component"]:c for c in d["core_components"]};push_by={c["component"]:c for c in d["push_components"]}
 for r in d["corridor_product_ribbons"]:
  c=[point(v) for v in core_by[r["component"]]["vertices"]];lo,hi=r["core_vertex_range"];vertices=c[lo:hi+1]+[point(v) for v in r["push_vertices"]]
  for local_index,ids in enumerate(r["ribbon_triangles"]):triangles.append((r["corridor_index"],local_index,tuple(vertices[i] for i in ids)))
 bounds=[bbox(t[2]) for t in triangles];projected_geometries=[projected_geometry(t[2]) for t in triangles];tree=STRtree(projected_geometries);broad=height_rejects=incidence_skips=projection_rejects=exact_triangle_checks=0
 for i,(_,_,first) in enumerate(triangles):
  if os.environ.get("T73_PROGRESS") and i%1000==0:print(f"triangles {i}/{len(triangles)} broad={broad} exact={exact_triangle_checks}",file=sys.stderr,flush=True)
  for raw in tree.query(projected_geometries[i],predicate="intersects"):
   j=int(raw)
   if j<=i:continue
   broad+=1;second=triangles[j][2]
   if bounds[i][1][2]<bounds[j][0][2] or bounds[j][1][2]<bounds[i][0][2] or bounds[i][4]<bounds[j][3] or bounds[j][4]<bounds[i][3]:height_rejects+=1;continue
   if set(first)&set(second):incidence_skips+=1;continue
   if not projected_triangles_intersect(first,second):projection_rejects+=1;continue
   exact_triangle_checks+=1
   if triangles_intersect(first,second):raise AssertionError(f"nonincident corridor ribbons intersect: {i}/{j}")
 segments=[]
 for name in core_by:
  for kind,c in (("core",core_by[name]),("push",push_by[name])):
   v=[point(x) for x in c["vertices"]]
   for a,b in zip(v,v[1:]):segments.append((kind,name,(a,b)))
 sbounds=[bbox(s[2]) for s in segments];segment_geometries=[projected_geometry(s[2]) for s in segments];stree=STRtree(segment_geometries);segment_broad=segment_height_rejects=segment_incidence_skips=segment_projection_rejects=exact_segment_checks=0
 for i,(_,_,triangle) in enumerate(triangles):
  for raw in stree.query(projected_geometries[i],predicate="intersects"):
   j=int(raw);segment_broad+=1;segment=segments[j][2]
   if bounds[i][1][2]<sbounds[j][0][2] or sbounds[j][1][2]<bounds[i][0][2] or bounds[i][4]<sbounds[j][3] or sbounds[j][4]<bounds[i][3]:segment_height_rejects+=1;continue
   if set(triangle)&set(segment):segment_incidence_skips+=1;continue
   if not projected_segment_triangle_intersect(segment,triangle):segment_projection_rejects+=1;continue
   exact_segment_checks+=1
   if segment_triangle(segment,triangle):raise AssertionError(f"corridor ribbon meets nonincident framed segment: {i}/{j}")
 return {"verdict":"PASS_AFFINE_S3_PRODUCT_CORRIDOR_RIBBON_GLOBAL_CLEARANCE","ribbon_triangles":len(triangles),"triangle_broad_candidates":broad,"triangle_height_rejects":height_rejects,"triangle_incidence_skips":incidence_skips,"triangle_projection_rejects":projection_rejects,"exact_triangle_triangle_checks":exact_triangle_checks,"framed_segments":len(segments),"segment_broad_candidates":segment_broad,"segment_height_rejects":segment_height_rejects,"segment_incidence_skips":segment_incidence_skips,"segment_projection_rejects":segment_projection_rejects,"exact_segment_triangle_checks":exact_segment_checks,"embedded_corridor_product_ribbons":True}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
