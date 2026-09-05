#!/usr/bin/env python3
"""Probe regular tilted projections of the complete affine framed link."""
from __future__ import annotations
import argparse,json,math
from collections import Counter
from fractions import Fraction
from pathlib import Path
from shapely.geometry import box
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_affine_s3_framed_realization.json";CORE=ROOT/"geometry/t73_affine_s3_core_realization.json"
def point(v):return tuple(Fraction(x) for x in v)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def curves(data):
 out=[]
 for c in data["dotted_components"]:out.append((c["component"],[point(v) for v in c["vertices"]]))
 for c in data["core_components"]:out.append((c["component"],[point(v) for v in c["vertices"]]))
 for c in data["push_components"]:out.append((c["component"]+"__push",[point(v) for v in c["vertices"]]))
 return out
def probe(q,mode="tilt"):
 data=json.loads(DATA.read_text());p=json.loads(CORE.read_text())["projection_denominator"];b1=(Fraction(1),0,Fraction(1,p));b2=(0,Fraction(1),Fraction(1,p**2));h=(Fraction(-1,p),Fraction(-1,p**2),Fraction(1));basis=(tuple(b1[i]+h[i]/q for i in range(3)),tuple(b2[i]+h[i]/q**2 for i in range(3)))
 if mode=="xz":basis=((Fraction(1),0,0),(0,0,Fraction(1)))
 elif mode=="yz":basis=((0,Fraction(1),0),(0,0,Fraction(1)))
 elif mode=="integer":basis=((Fraction(1),Fraction(2),Fraction(3)),(Fraction(4),Fraction(5),Fraction(7)))
 seg=[]
 for owner,vs in curves(data):
  n=len(vs)-1
  for i,(a,b) in enumerate(zip(vs,vs[1:])):
   pa=(dot(basis[0],a),dot(basis[1],a));pb=(dot(basis[0],b),dot(basis[1],b))
   if pa==pb:return {"denominator":q,"mode":mode,"collapsed_segment":[owner,i]}
   seg.append((owner,i,n,pa,pb))
 boxes=[]
 for _,_,_,a,b in seg:boxes.append(box(math.nextafter(float(min(a[0],b[0])),-math.inf),math.nextafter(float(min(a[1],b[1])),-math.inf),math.nextafter(float(max(a[0],b[0])),math.inf),math.nextafter(float(max(a[1],b[1])),math.inf)))
 tree=STRtree(boxes);count=0;owners=Counter()
 for i,b in enumerate(boxes):
  o,si,n,_,_=seg[i]
  for raw in tree.query(b):
   j=int(raw)
   if j<=i:continue
   p2,sj,_,_,_=seg[j]
   if o==p2 and ((si-sj)%n in (0,1,n-1)):continue
   count+=1;owners["/".join(sorted((o,p2)))]+=1
 return {"denominator":q,"segments":len(seg),"broad_candidates":count,"owner_pair_broad_candidates":dict(owners),"projection_basis":[[str(x) for x in row] for row in basis],"height_covector":[str(x) for x in h],"status":"NO_COLLAPSED_SEGMENTS_BROAD_PHASE_COUNTED"}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--denominator",type=int,default=1000033);p.add_argument("--mode",choices=("tilt","xz","yz","integer"),default="tilt");a=p.parse_args();print(json.dumps(probe(a.denominator,a.mode),sort_keys=True))
