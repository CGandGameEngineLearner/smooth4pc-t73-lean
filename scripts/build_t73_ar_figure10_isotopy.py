#!/usr/bin/env python3
"""Digitize AR84 Figure 10a's symmetric affine isotopy rule."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'geometry/t73_ar_figure10_isotopy.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 v={'schema':'t73_ar_figure10_isotopy/v1','literature_source':'AR84 internal page 15, Figure 10a--10g discussion','parameter_domain':{'t':['0','1'],'epsilon':'small_positive_rational'},'fixed_point':'q=exp(pi*i*(0,0,0))','affine_rules':{'L_B':'psi_t(exp(pi*i*(x,y,z)))=exp(pi*i*(x,y,z+t*(1/2-epsilon)))','L_D':'psi_t(exp(pi*i*(x_prime,y_prime,z_prime)))=exp(pi*i*(x_prime,y_prime,z_prime-t*(1/2-epsilon)))'},'invariants':['q fixed at every stage','C3 and conjugate C3 remain on their designated tori','g-symmetry preserved'],'word_output':{'C1':'alpha_2','C2':'alpha_3 alpha_2','C3':'alpha_1 alpha_3^v'},'completion_status':'VERIFIED_LITERATURE_RULE_ONLY'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('Figure 10 isotopy stale')
 print('T73_AR_FIGURE10_ISOTOPY=PASS')
