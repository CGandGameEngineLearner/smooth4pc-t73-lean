#!/usr/bin/env python3
"""Find low-work regular projection candidates for each core/product-push pair."""
from __future__ import annotations
import argparse,json,math
from fractions import Fraction
from pathlib import Path
from shapely.geometry import box
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];RECEIPT=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json"
CANDIDATES={"xy":((1,0,0),(0,1,0)),"xz":((1,0,0),(0,0,1)),"yz":((0,1,0),(0,0,1)),"a":((1,1,0),(0,0,1)),"b":((1,0,1),(0,1,0)),"c":((0,1,1),(1,0,0)),"d":((1,2,3),(2,-3,1)),"e":((2,3,5),(7,11,13)),"f":((1,5,2),(3,1,7))}
def point(v):return tuple(Fraction(x) for x in v)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def boxes(vertices,basis):
 out=[]
 for a,b in zip(vertices,vertices[1:]):
  p=(dot(basis[0],a),dot(basis[1],a));q=(dot(basis[0],b),dot(basis[1],b))
  if p==q:return None
  out.append(box(math.nextafter(float(min(p[0],q[0])),-math.inf),math.nextafter(float(min(p[1],q[1])),-math.inf),math.nextafter(float(max(p[0],q[0])),math.inf),math.nextafter(float(max(p[1],q[1])),math.inf)))
 return out
def probe(component):
 receipt=json.loads(RECEIPT.read_text());d=json.loads(resolve(receipt["cache_path"]).read_text());core=next(c for c in d["core_components"] if c["component"]==component);push=next(c for c in d["push_components"] if c["component"]==component);cv=[point(v) for v in core["vertices"]];pv=[point(v) for v in push["vertices"]];results=[]
 for name,raw in CANDIDATES.items():
  basis=tuple(tuple(Fraction(x) for x in row) for row in raw);a=boxes(cv,basis);b=boxes(pv,basis)
  if a is None or b is None:results.append({"name":name,"status":"COLLAPSED"});continue
  tree=STRtree(b);count=sum(len(tree.query(x)) for x in a);results.append({"name":name,"status":"NONCOLLAPSED","broad_candidates":count,"basis":[list(row) for row in raw]})
 return {"component":component,"core_segments":len(cv)-1,"push_segments":len(pv)-1,"results":results,"best":min((x for x in results if x["status"]=="NONCOLLAPSED"),key=lambda x:x["broad_candidates"])}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("component",choices=("m_2","m_3","r_xy","r_yz","r_zx"));a=p.parse_args();print(json.dumps(probe(a.component),sort_keys=True))
