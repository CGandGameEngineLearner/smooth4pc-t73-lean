#!/usr/bin/env python3
"""Build a rational candidate lane family from actual y cuts to AR y feet."""
from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
CUT=ROOT/'geometry/t73_actual_cut_tangle.json'; CHART=ROOT/'geometry/t73_unified_kirby_foot_chart.json'; OUT=ROOT/'geometry/t73_y_foot_lane_candidate.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def enc(p):return [str(x) for x in p]
def build():
 cut=json.loads(CUT.read_text()); chart=json.loads(CHART.read_text()); y=next(h for h in chart['handles'] if h['name']=='y')['foot_pair']
 center=tuple(Fraction(x) for x in y['positive_center']); radius=Fraction(y['radius']); passages=cut['passages']; targets=[]
 for i in range(len(passages)):
  r=Fraction(i+1,len(passages)+1); u=2*r/(1+r*r); v=(1-r*r)/(1+r*r); targets.append((center[0]+radius*u,center[1]+radius*v,center[2]))
 numeric=np.array([[float(x) for x in p] for p in targets]); distances=np.linalg.norm(numeric[:,None]-numeric[None,:],axis=2); np.fill_diagonal(distances,np.inf)
 if not np.all(distances>0):raise AssertionError('candidate foot targets collide')
 lanes=[]
 for i,(passage,target) in enumerate(zip(passages,targets)):
  source=tuple(Fraction(x) for x in passage['cut_arc_in_ball'][1]); level=Fraction(i+1,len(passages)+1)
  vertices=[(*source,Fraction(0)),(*source,level),(*target,level)]
  normal=tuple(Fraction(x) for x in passage['product_normal'])+(Fraction(0),)
  lanes.append({'wicket':passage['wicket'],'owner':passage['owner'],'orientation':passage['orientation'],'source_id':passage['source_id'],'vertices':[enc(p) for p in vertices],'foot_boundary_target':enc(target),'height_layer':str(level),'framing_rectangle':[enc(vertices[1]),enc(vertices[2]),enc(tuple(vertices[2][j]+normal[j] for j in range(4))),enc(tuple(vertices[1][j]+normal[j] for j in range(4)))],'status':'CANDIDATE_UNVERIFIED'})
 v={'schema':'t73_y_foot_lane_candidate/v1','cut_tangle_sha256':cut['sha256'],'foot_chart_sha256':chart['sha256'],'lanes':lanes,'numpy_prefilter':'pairwise target distances positive','completion_status':'CANDIDATE_UNVERIFIED'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('y foot lane candidate stale')
 print(f"T73_Y_FOOT_LANES=CANDIDATE_UNVERIFIED count={len(v['lanes'])}")
