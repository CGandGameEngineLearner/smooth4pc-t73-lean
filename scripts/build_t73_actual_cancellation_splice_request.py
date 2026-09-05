#!/usr/bin/env python3
"""Inventory every t/x cancellation band that needs geometric splice data."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'geometry/t73_cancel_t_hcs.json'; X=ROOT/'geometry/t73_cancel_x_m1.json'
OUT=ROOT/'geometry/t73_actual_cancellation_splice_request.json'
def sha(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def rows(kind,data,key):
    return [{'index':i,'center_path_sha256':sha(b[key]),'width':b['band_width'],'required':['left_boundary_edge','right_boundary_edge','source_attachment_parameter','target_attachment_parameter','parallel_replacement_arc','spliced_successor']} for i,b in enumerate(data['slide_bands'])]
def build():
    t=json.loads(T.read_text()); x=json.loads(X.read_text())
    result={'schema':'t73_actual_cancellation_splice_request/v1','t_cancellation_sha256':t['sha256'],'x_cancellation_sha256':x['sha256'],'t_bands':rows('t',t,'band_core_on_belt_sphere'),'x_bands':rows('x',x,'band_core_on_positive_belt_face'),'completion_status':'OPEN'}
    if len(result['t_bands'])!=6 or len(result['x_bands'])!=1513: raise AssertionError('unexpected cancellation band count')
    result['sha256']=sha(result); return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
    if a.write: OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    if a.check and json.loads(OUT.read_text())!=v: raise AssertionError('splice request stale')
    print('T73_CANCELLATION_SPLICE_REQUEST=OPEN')
if __name__=='__main__':main()
