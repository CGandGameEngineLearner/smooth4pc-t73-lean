#!/usr/bin/env python3
"""Independently check exact source/target invariants of candidate y-foot lanes."""
from __future__ import annotations
import json
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LANES=ROOT/'geometry/t73_y_foot_lane_candidate.json'; CUT=ROOT/'geometry/t73_actual_cut_tangle.json'
def verify():
 data=json.loads(LANES.read_text());cut=json.loads(CUT.read_text()); source={p['wicket']:p for p in cut['passages']}
 if data['completion_status']!='CANDIDATE_UNVERIFIED':raise AssertionError('candidate promoted')
 if len(data['lanes'])!=44 or set(p['wicket'] for p in data['lanes'])!=set(source):raise AssertionError('wicket coverage')
 targets=set();levels=set()
 for lane in data['lanes']:
  original=source[lane['wicket']]
  if any(lane[k]!=original[k] for k in ('owner','orientation','source_id')):raise AssertionError('source binding')
  if [str(Fraction(x)) for x in lane['vertices'][0][:3]]!=original['cut_arc_in_ball'][1]:raise AssertionError('cut endpoint changed')
  target=tuple(lane['foot_boundary_target']);level=Fraction(lane['height_layer'])
  if target in targets or level in levels:raise AssertionError('nonunique candidate routing')
  targets.add(target);levels.add(level)
  if Fraction(lane['framing_rectangle'][2][3])!=level:raise AssertionError('framing changed height layer')
 return {'verdict':'PASS_CANDIDATE_INVARIANTS_ONLY','lanes':44}
if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
