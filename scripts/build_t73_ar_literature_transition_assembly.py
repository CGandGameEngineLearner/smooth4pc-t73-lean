#!/usr/bin/env python3
"""Assemble independently digitized AR literature cells for T73."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES={name:ROOT/'geometry'/file for name,file in {'canonical':'t73_ar_canonical_straightening.json','feet':'t73_ar_foot_pairing_model.json','fixed':'t73_ar_figure5_fixed_points.json','figure9':'t73_ar_figure9_factorization.json','figure10':'t73_ar_figure10_isotopy.json'}.items()}
OUT=ROOT/'geometry/t73_ar_literature_transition_assembly.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 d={k:json.loads(p.read_text()) for k,p in FILES.items()}
 if d['canonical']['ar_canonical_matrix']!=d['figure9']['ar_canonical_matrix']:raise AssertionError('canonical matrix mismatch')
 if not any(p['id']=='q' and p['torus_half_coordinates']==[0,0,0] for p in d['fixed']['fixed_points']):raise AssertionError('fixed point q missing')
 v={'schema':'t73_ar_literature_transition_assembly/v1','artifact_sha256s':{k:d[k]['sha256'] for k in d},'canonical_parameters':d['canonical']['parameters'],'fixed_point_q':[0,0,0],'cells':['AR84 Figure 2a antipodal foot/reflection model','AR84 Figure 5 involution/fixed-point model','AR84 Figure 9 surgery factorization','AR84 Figure 10 affine isotopy'],'next_required_binding':'map all four foot pairs and every band boundary to the actual AR/cancellation lanes','completion_status':'VERIFIED_LITERATURE_CELLS_ONLY'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('literature assembly stale')
 print('T73_AR_LITERATURE_ASSEMBLY=PASS')
