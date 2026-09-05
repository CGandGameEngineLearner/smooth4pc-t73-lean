#!/usr/bin/env python3
"""Fail-closed validator for the actual AR cut-and-surgery witness."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WITNESS=ROOT/'geometry/t73_ar_to_kirby_presentation.json'
AR=ROOT/'geometry/t73_actual_ar_link.json'
T=ROOT/'geometry/t73_cancel_t_hcs.json'
X=ROOT/'geometry/t73_cancel_x_m1.json'
SCHEMA=ROOT/'data/T73_AR_TO_KIRBY_PRESENTATION.schema.json'

def verify():
    if not WITNESS.exists(): return {'verdict':'OPEN','reason':'missing t73_ar_to_kirby_presentation witness'}
    import jsonschema
    value=json.loads(WITNESS.read_text(encoding='utf-8'))
    jsonschema.validate(value,json.loads(SCHEMA.read_text(encoding='utf-8')))
    bindings=value['source_bindings']
    expected={'actual_ar_link_sha256':json.loads(AR.read_text())['sha256'],'t_cancellation_sha256':json.loads(T.read_text())['sha256'],'x_cancellation_sha256':json.loads(X.read_text())['sha256']}
    if bindings!=expected: raise AssertionError('AR-to-Kirby witness source bindings are stale')
    names=[item.get('name') for item in value['post_cancellation_components']]
    if names!=['m_2','m_3','r_xy','r_yz','r_zx','dotted_y','dotted_z']: raise AssertionError('post-cancellation components are not the seven-component Kirby contract')
    return {'verdict':'PASS_WITNESS_SHAPE_ONLY','band_rectangles':len(value['band_rectangles']),'surgery_splices':len(value['surgery_splices'])}

if __name__=='__main__': print(json.dumps(verify(),sort_keys=True))
