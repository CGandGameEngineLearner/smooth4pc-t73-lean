#!/usr/bin/env python3
"""Normalize legacy band centerlines into a declared candidate 4D chart."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'geometry/t73_cancel_t_hcs.json';X=ROOT/'geometry/t73_cancel_x_m1.json';OUT=ROOT/'geometry/t73_candidate_band_chart_normalization.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def lift_t(p): return p if len(p)==4 else [*p,'1/2']
def lift_x(p):
    if len(p)==4:return p
    if len(p)!=3:raise AssertionError('unexpected x-band coordinate arity')
    return ['2',p[0],p[1],str(Fraction(1,2)+Fraction(p[2]))]
def build():
 t=json.loads(T.read_text());x=json.loads(X.read_text())
 rows=[]
 for kind,data,key,lift,formula in [('t',t,'band_core_on_belt_sphere',lift_t,'(x,y,z)->(x,y,z,1/2)'),('x',x,'band_core_on_positive_belt_face',lift_x,'(y,z,nu)->(2,y,z,1/2+nu)')]:
  for b in data['slide_bands']:
   rows.append({'kind':kind,'index':b['index'],'raw_centerline':b[key],'candidate_centerline_T3xI':[lift(p) for p in b[key]],'lift_formula':formula,'status':'CANDIDATE_UNVERIFIED'})
 v={'schema':'t73_candidate_band_chart_normalization/v1','t_cancellation_sha256':t['sha256'],'x_cancellation_sha256':x['sha256'],'bands':rows,'scope':'candidate coordinate lifts only; not an actual chart transition','status':'CANDIDATE_UNVERIFIED'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('candidate normalization stale')
 print('T73_CANDIDATE_BAND_NORMALIZATION=CANDIDATE_UNVERIFIED')
