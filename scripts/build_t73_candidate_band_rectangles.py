#!/usr/bin/env python3
"""Generate rational candidate rectangles and push-offs for every band centerline."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NORM=ROOT/'geometry/t73_candidate_band_chart_normalization.json'; T=ROOT/'geometry/t73_cancel_t_hcs.json'; X=ROOT/'geometry/t73_cancel_x_m1.json'; OUT=ROOT/'geometry/t73_candidate_band_rectangles.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def enc(p):return [str(x) for x in p]
def add(p,d):return tuple(a+b for a,b in zip(p,d))
def build():
 n=json.loads(NORM.read_text()); widths={('t',b['index']):Fraction(b['band_width']) for b in json.loads(T.read_text())['slide_bands']}|{('x',b['index']):Fraction(b['band_width']) for b in json.loads(X.read_text())['slide_bands']}
 rows=[]
 for b in n['bands']:
  points=[tuple(Fraction(x) for x in z) for z in b['candidate_centerline_T3xI']]
  w=widths[(b['kind'],b['index'])]; normal=(Fraction(0),w,Fraction(0),Fraction(0)); push=(Fraction(0),Fraction(0),w,Fraction(0))
  for segment_index,(p,q) in enumerate(zip(points,points[1:])):
   a,c=add(p,normal),add(q,normal); d,e=add(p,tuple(-x for x in normal)),add(q,tuple(-x for x in normal))
   rows.append({'kind':b['kind'],'index':b['index'],'segment_index':segment_index,'centerline': [enc(p),enc(q)],'normal':enc(normal),'band_vertices':[enc(a),enc(c),enc(e),enc(d)],'band_triangles':[[0,1,2],[0,2,3]],'band_boundary':[[0,1],[3,2],[0,3],[1,2]],'longitudinal_edges':[[0,1],[3,2]],'push_off_vertices':[enc(add(v,push)) for v in (a,c,e,d)],'status':'CANDIDATE_UNVERIFIED'})
 v={'schema':'t73_candidate_band_rectangles/v1','normalization_sha256':n['sha256'],'bands':rows,'status':'CANDIDATE_UNVERIFIED'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('candidate rectangles stale')
 print(f"T73_CANDIDATE_BAND_RECTANGLES=CANDIDATE_UNVERIFIED count={len(v['bands'])}")
