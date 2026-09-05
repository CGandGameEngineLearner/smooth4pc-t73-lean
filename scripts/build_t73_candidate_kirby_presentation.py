#!/usr/bin/env python3
"""Generate a declared, non-actual seven-component Kirby exploration input."""
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'geometry/t73_candidate_kirby_presentation.json'
AR=ROOT/'geometry/t73_actual_ar_link.json'; T=ROOT/'geometry/t73_cancel_t_hcs.json'; X=ROOT/'geometry/t73_cancel_x_m1.json'
def load_fixture():
 p=ROOT/'scripts/build_t73_full_handle_diagram_example.py';s=importlib.util.spec_from_file_location('fixture',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 value=load_fixture().build()
 value['purpose']='algorithmic candidate Kirby presentation; not an AR cut-and-surgery witness'
 value['candidate_status']='CANDIDATE_UNVERIFIED'
 value['provenance']={'actual_ar_link_sha256':json.loads(AR.read_text())['sha256'],'t_cancellation_sha256':json.loads(T.read_text())['sha256'],'x_cancellation_sha256':json.loads(X.read_text())['sha256'],'choice_rule':'separated rational Reidemeister-I component model; no claimed relative AR equivalence'}
 value['sha256']=sha(value)
 return value
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('candidate Kirby input is stale')
 print('T73_CANDIDATE_KIRBY_PRESENTATION=CANDIDATE_UNVERIFIED')
