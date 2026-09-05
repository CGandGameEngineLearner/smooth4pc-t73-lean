#!/usr/bin/env python3
"""Digitize AR84 page 14 Figure 9 matrix factorization for T73."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'geometry/t73_ar_figure9_factorization.json'
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 canonical=[[0,0,1],[189,41,0],[1240,269,32]];left=[[1,0,0],[1,1,0],[1,1,1]];right=[[1,0,0],[-1,1,0],[0,-1,1]]
 result=mm(mm(left,canonical),right)
 expected=[[0,-1,1],[148,40,1],[1119,277,33]]
 if result!=expected:raise AssertionError('AR Figure 9 factorization mismatch')
 v={'schema':'t73_ar_figure9_factorization/v1','literature_source':'AR84 internal page 14, Figure 9a/9b discussion','ar_canonical_matrix':canonical,'left_elementary_matrix':left,'right_elementary_matrix':right,'t73_surgery_description_matrix':result,'interpretation':'Figure 9 relates the solid torus T_G to the surgery description of S3; sliding T_G off the link produces the knot description','completion_status':'VERIFIED_LITERATURE_MATRIX_EXTRACTION_ONLY'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('Figure 9 factorization stale')
 print('T73_AR_FIGURE9_FACTORIZATION=PASS')
