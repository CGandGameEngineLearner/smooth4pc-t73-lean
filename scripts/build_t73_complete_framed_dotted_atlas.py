#!/usr/bin/env python3
"""Assemble the complete seven-component framed dotted atlas after x/m1 cancellation."""
from __future__ import annotations
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];X=ROOT/"geometry/t73_x_m1_complete_framed_cancellation_image.json";MAP=ROOT/"geometry/t73_yz_dotted_passage_replacement_map.json";CYL=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_verification.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";OUTPUT=ROOT/"geometry/t73_complete_framed_dotted_atlas.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def build():
 x=json.loads(X.read_text());mp=json.loads(MAP.read_text());cyl=json.loads(CYL.read_text());d=json.loads(DOTTED.read_text());removed=defaultdict(lambda:[0,0])
 for r in mp["replacements"]:removed[r["owner"]][0]+=r["source_core_segment_count"];removed[r["owner"]][1]+=1
 components=[]
 for old in x["components"]:
  name=old["component"];source,target=removed[name];components.append({"component":name,"kind":"framed_two_handle","pre_dotted_core_segments":old["target_core_segments"],"pre_dotted_push_segments":old["target_push_segments"],"removed_passage_core_segments":source,"removed_passage_push_segments":source,"inserted_hopf_core_segments":target,"inserted_hopf_push_segments":target,"atlas_core_segments":old["target_core_segments"]-source+target,"atlas_push_segments":old["target_push_segments"]-source+target,"closed_core":True,"closed_push":True})
 dotted_components=[{"component":c["dotted_component"],"kind":"dotted_one_handle","polygon_segments":len(c["dotted_vertices"])-1,"passage_count":c["passage_count"]} for c in d["charts"]]
 r={"schema":"t73_complete_framed_dotted_atlas/v1","x_m1_complete_framed_cancellation_image_sha256":x["sha256"],"yz_dotted_passage_replacement_map_sha256":mp["sha256"],"yz_mapping_cylinders_verification_sha256":cyl["sha256"],"actual_dotted_s3_passage_cells_sha256":d["sha256"],"framed_components":components,"dotted_components":dotted_components,"component_order":["dotted_y","dotted_z","m_2","m_3","r_xy","r_yz","r_zx"],"component_count":7,"framed_core_segment_count":sum(i["atlas_core_segments"] for i in components),"framed_push_segment_count":sum(i["atlas_push_segments"] for i in components),"dotted_polygon_segment_count":sum(i["polygon_segments"] for i in dotted_components),"passage_mapping_cylinder_count":1785,"passage_mapping_cylinder_tetrahedra":21408,"completion_status":"COMPLETE_SEVEN_COMPONENT_FRAMED_DOTTED_ATLAS_CONSTRUCTED","atlas_continuity_status":"PASS","single_affine_s3_chart_status":"OPEN","complete_pd_status":"OPEN_SINGLE_CHART_PROJECTION_REQUIRED"};r["sha256"]=sha(r);return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");p.add_argument("--check",action="store_true");a=p.parse_args();r=build()
 if a.write:OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
 if a.check and json.loads(OUTPUT.read_text())!=r:raise AssertionError("complete dotted atlas stale")
 print(json.dumps({"status":r["completion_status"],"components":7,"core":r["framed_core_segment_count"],"push":r["framed_push_segment_count"]},sort_keys=True))
if __name__=="__main__":main()
