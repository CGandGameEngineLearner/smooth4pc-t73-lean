#!/usr/bin/env python3
"""Verify the exact T73 conjugacy to AR Lemma 3.2 canonical form."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'geometry/t73_ar_canonical_straightening.json'
A=[[0,269,1240],[0,41,189],[1,0,32]];P=[[32,0,-1],[0,-1,0],[-1,0,0]];C=[[0,0,1],[189,41,0],[1240,269,32]]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def det(a):return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 if det(P)!=1 or mm(A,P)!=mm(P,C):raise AssertionError('T73 AR canonical conjugacy failed')
 v={'schema':'t73_ar_canonical_straightening/v1','matrix_A':A,'conjugating_matrix_P':P,'ar_canonical_matrix':C,'parameters':{'m':189,'lambda':41,'n':1240,'p':269,'v':32,'a':73},'literature_source':'AR84 Lemma 3.2, internal pages 11-12','verification':'A P = P C and det(P)=1','completion_status':'VERIFIED_MATRIX_CONJUGACY_ONLY'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('AR straightening stale')
 print('T73_AR_CANONICAL_CONJUGACY=PASS')
