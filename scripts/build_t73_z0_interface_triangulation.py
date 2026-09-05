#!/usr/bin/env python3
"""Build the exact common z=0 interface triangulation with four hole loops."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'geometry/t73_selected_source_exterior.json'
OUTPUT=ROOT/'geometry/t73_z0_interface_triangulation.json'

def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()

def build():
    source=json.loads(SOURCE.read_text(encoding='utf-8'))
    xs=[-20,-7,-5,5,7,20]; ys=[-20,-7,-5,5,7,20]
    vertices=[[str(x),str(y),'0'] for y in ys for x in xs]
    index=lambda x,y:y*len(xs)+x
    holes={(1,1),(1,3),(3,1),(3,3)}
    triangles=[]
    for y in range(5):
        for x in range(5):
            if (x,y) in holes: continue
            a,b,c,d=index(x,y),index(x+1,y),index(x+1,y+1),index(x,y+1)
            triangles.extend([[a,b,c],[a,c,d]])
    value={'schema':'t73_z0_interface_triangulation/v1','source_exterior_sha256':source['sha256'],'vertices':vertices,'triangles':triangles,'hole_cells':sorted([list(x) for x in holes]),'outer_bounds':['-20','20','-20','20'],'sha256':None}
    value['sha256']=sha({k:v for k,v in value.items() if k!='sha256'})
    return value

def main():
    p=argparse.ArgumentParser(); p.add_argument('--write',action='store_true'); p.add_argument('--check',action='store_true'); a=p.parse_args(); value=build()
    if a.write: OUTPUT.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    if a.check and json.loads(OUTPUT.read_text(encoding='utf-8'))!=value: raise AssertionError('interface triangulation is stale')
    print(f"T73_Z0_INTERFACE=PASS vertices={len(value['vertices'])} triangles={len(value['triangles'])}")
if __name__=='__main__': main()
