#!/usr/bin/env python3
"""Group candidate rectangle segments into ordered candidate PL band strips."""
from __future__ import annotations
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; IN=ROOT/'geometry/t73_candidate_band_rectangles.json'; OUT=ROOT/'geometry/t73_candidate_band_splice_descriptors.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 data=json.loads(IN.read_text()); groups=defaultdict(list)
 for r in data['bands']:groups[(r['kind'],r['index'])].append(r)
 bands=[]
 for (kind,index),rows in sorted(groups.items()):
  rows.sort(key=lambda r:r['segment_index'])
  for a,b in zip(rows,rows[1:]):
   if a['centerline'][1]!=b['centerline'][0]:raise AssertionError('band segments do not join')
  bands.append({'kind':kind,'index':index,'segment_count':len(rows),'segment_indices':[r['segment_index'] for r in rows],'source_attachment':{'point':rows[0]['centerline'][0],'parameter':'0'},'target_attachment':{'point':rows[-1]['centerline'][1],'parameter':'1'},'splice_order':'concatenate ordered centerline segments and retain both longitudinal boundary lanes','status':'CANDIDATE_UNVERIFIED'})
 if len(bands)!=1519:raise AssertionError('candidate band count changed')
 v={'schema':'t73_candidate_band_splice_descriptors/v1','rectangles_sha256':data['sha256'],'bands':bands,'status':'CANDIDATE_UNVERIFIED'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('candidate splice descriptors stale')
 print(f"T73_CANDIDATE_BAND_SPLICES=CANDIDATE_UNVERIFIED count={len(v['bands'])}")
