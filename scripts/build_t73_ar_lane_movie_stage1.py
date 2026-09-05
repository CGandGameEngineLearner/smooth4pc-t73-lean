#!/usr/bin/env python3
"""Bind documented T73 t/x/y passage anchors to the unified foot chart."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BELTS=ROOT/'geometry/t73_belt_spheres.json';CUT=ROOT/'geometry/t73_actual_cut_tangle.json';CHART=ROOT/'geometry/t73_unified_kirby_foot_chart.json';OUT=ROOT/'geometry/t73_ar_lane_movie_stage1.json'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()
def build():
 belts=json.loads(BELTS.read_text());cut=json.loads(CUT.read_text());chart=json.loads(CHART.read_text())
 anchors=[]
 for handle,key in [('t','t_handle'),('x','x_handle')]:
  for i,p in enumerate(belts[key]['passages']):
   anchors.append({'handle':handle,'anchor_index':i,'component':p['component'],'orientation':p['orientation'],'source_id':p.get('source_id',p.get('arc')),'belt_point':p.get('point_on_belt',p.get('belt_face_point',p.get('intersection_points'))),'binding_status':'BOUND_TO_T73_BELT_GEOMETRY'})
 for p in cut['passages']:
  anchors.append({'handle':'y','anchor_index':p['wicket'],'component':p['owner'],'orientation':p['orientation'],'source_id':p['source_id'],'belt_point':p['belt_face_point'],'cut_arc_in_ball':p['cut_arc_in_ball'],'product_normal':p['product_normal'],'binding_status':'BOUND_TO_T73_CUT_TANGLE'})
 v={'schema':'t73_ar_lane_movie_stage1/v1','belt_spheres_sha256':belts['sha256'],'cut_tangle_sha256':cut['sha256'],'foot_chart_sha256':chart['sha256'],'anchors':anchors,'counts':{'t':len(belts['t_handle']['passages']),'x':len(belts['x_handle']['passages']),'y':len(cut['passages']),'z':0},'z_status':'OPEN_T73_LANE_BINDING','completion_status':'PARTIAL_ANCHORS_ONLY'};v['sha256']=sha(v);return v
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();v=build()
 if a.write:OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
 if a.check and json.loads(OUT.read_text())!=v:raise AssertionError('lane stage1 stale')
 print('T73_AR_LANE_MOVIE_STAGE1=PARTIAL_ANCHORS_ONLY')
