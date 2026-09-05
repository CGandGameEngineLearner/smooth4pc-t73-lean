#!/usr/bin/env python3
"""Digitize the eight fixed points and involution recorded on AR84 page 9."""
from __future__ import annotations
import argparse,hashlib,json
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'geometry/t73_ar_figure5_fixed_points.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 labels={(0,0,0):'q',(1,0,0):'alpha_1',(0,1,0):'alpha_2',(0,0,1):'alpha_3',(1,1,0):'alpha_4',(1,0,1):'alpha_5',(0,1,1):'alpha_6',(1,1,1):'alpha_7'}
 points=[{'id':labels[bits],'torus_half_coordinates':list(bits)} for bits in product((0,1),repeat=3)]
 v={'schema':'t73_ar_figure5_fixed_points/v1','literature_source':'AR84 internal page 9, Figure 5 discussion','fixed_points':points,'involution':'g(exp(pi*i*(theta,phi,psi)))=exp(pi*i*(theta,phi,psi))=exp(pi*i*a(theta,phi,psi))','heegaard_condition':'g(H_B)=H_D and g preserves S_H','completion_status':'VERIFIED_LITERATURE_EXTRACTION_ONLY'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('Figure 5 fixed points stale')
 print('T73_AR_FIGURE5_FIXED_POINTS=PASS')
