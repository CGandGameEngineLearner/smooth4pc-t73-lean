#!/usr/bin/env python3
"""Assemble the 1513 x-cancellation bands into a candidate PL movie."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECT=ROOT/'geometry/t73_candidate_band_rectangles.json'; SPLICE=ROOT/'geometry/t73_candidate_band_splice_descriptors.json'; SOURCE=ROOT/'geometry/t73_cancel_x_m1.json'; OUT=ROOT/'geometry/t73_candidate_x_band_movie.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 rect=json.loads(RECT.read_text());splice=json.loads(SPLICE.read_text());source=json.loads(SOURCE.read_text())
 by={};
 for r in rect['bands']:
  if r['kind']=='x':by.setdefault(r['index'],[]).append(r)
 desc={i['index']:i for i in splice['bands'] if i['kind']=='x'};movie=[]
 for b in source['slide_bands']:
  i=b['index'];segments=sorted(by[i],key=lambda x:x['segment_index']);d=desc[i]
  if len(segments)!=d['segment_count']:raise AssertionError('x segment count mismatch')
  movie.append({'index':i,'component':b['component'],'movie_time_order':b['movie_time_order'],'current_link_before':f'candidate_x_state_{i}','source_attachment':d['source_attachment'],'target_attachment':d['target_attachment'],'rectangle_segments':segments,'splice':d,'updated_link_after':f'candidate_x_state_{i+1}','status':'CANDIDATE_UNVERIFIED'})
 if len(movie)!=1513 or [m['movie_time_order'] for m in movie]!=list(range(1513)):raise AssertionError('x movie order')
 v={'schema':'t73_candidate_x_band_movie/v1','x_cancellation_sha256':source['sha256'],'rectangles_sha256':rect['sha256'],'splices_sha256':splice['sha256'],'bands':movie,'completion_status':'CANDIDATE_UNVERIFIED'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('candidate x movie stale')
 print('T73_CANDIDATE_X_BAND_MOVIE=CANDIDATE_UNVERIFIED')
