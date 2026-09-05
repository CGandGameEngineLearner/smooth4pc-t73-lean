#!/usr/bin/env python3
"""Realise AR Figure 2a handle feet as disjoint rational antipodal balls."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'geometry/t73_ar_foot_pairing_model.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def enc(p):return [str(x) for x in p]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def build():
 centers=[(Fraction(1),0,0),(0,Fraction(1),0),(0,0,Fraction(1)),(Fraction(1,3),Fraction(2,3),Fraction(2,3))]
 radius=Fraction(1,20)
 if any(dot(p,p)!=1 for p in centers):raise AssertionError('feet are not on unit sphere')
 if any(sum((a[i]-b[i])**2 for i in range(3)) <= (2*radius)**2 for n,a in enumerate(centers) for b in centers[n+1:]):raise AssertionError('foot balls meet')
 feet=[]
 for i,b in enumerate(centers):feet.append({'handle_index':i,'positive_center':enc(b),'negative_center':enc(tuple(-x for x in b)),'radius':str(radius),'boundary_identification':'reflection in plane through origin perpendicular to positive_center','reflection_matrix':[[str((1 if r==c else 0)-2*b[r]*b[c]) for c in range(3)] for r in range(3)]})
 v={'schema':'t73_ar_foot_pairing_model/v1','literature_source':'AR84 Figure 2a, internal page 5','feet':feet,'status':'VERIFIED_GENERIC_FOOT_MODEL_ONLY','t73_lane_binding':'OPEN'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('AR foot model stale')
 print('T73_AR_FOOT_PAIRING_MODEL=PASS_GENERIC_ONLY')
