#!/usr/bin/env python3
"""Save citable, non-copyright-reproducing sources for T73 PL reconstruction."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'geometry/t73_literature_geometry_ledger.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 v={'schema':'t73_literature_geometry_ledger/v1','sources':[
 {'id':'AR84_section4','citation':'Aitchison--Rubinstein, Fibered knots and involutions on homotopy spheres (1984), Section 4','url':'https://math.berkeley.edu/~kirby/papers/Gordon%20and%20Kirby%20%28editors%29%20-%20Four-manifold%20theory%20%28Durham%29%20-%20MR0780574.pdf','pages':['13','14'],'anchors':['Theorem 4.1','Figure 5','Figure 9a','Figure 9b','Figure 10a'],'supports':['Cappell--Shaneson handle decomposition','geometric 2/1 cancellation','branched-cover/Kirby link description','symmetric straightening'],'does_not_supply':['T73 rational coordinates','machine-readable foot pairing','per-band boundary edges','1513 x-band movie']},
 {'id':'Johnson2011','citation':'Jesse Johnson, Automorphisms of the three-torus preserving a genus-three Heegaard splitting (2011)','url':'https://arxiv.org/abs/0708.2683','anchors':['eight-element generating set'],'supports':['Heegaard-preserving generator representatives'],'does_not_supply':['T73 93-factor coordinate movie','Kirby band data']},
 {'id':'MWW2023','citation':'Manolescu--Walker--Wedrich, Skein lasagna modules and handle decompositions (2023)','url':'https://arxiv.org/abs/2206.04616','anchors':['Theorems 3.7, 3.10, 4.7'],'supports':['handle attachment/coequalizer formulas'],'does_not_supply':['candidate-specific Kirby or foam chain maps']}
 ],'digitisation_pipeline':['cite source operation','encode rational PL cell','verify local boundary/framing','compose into kappa_AR','compare to AR source bindings'],'completion_status':'OPEN'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('literature ledger stale')
 print('T73_LITERATURE_GEOMETRY_LEDGER=OPEN')
