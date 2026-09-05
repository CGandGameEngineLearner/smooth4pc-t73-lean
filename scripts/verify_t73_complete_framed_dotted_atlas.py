#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/"geometry/t73_complete_framed_dotted_atlas.json";X=ROOT/"geometry/t73_x_m1_complete_framed_cancellation_image.json";MAP=ROOT/"geometry/t73_yz_dotted_passage_replacement_map.json";CYL=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_verification.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def verify():
 d=json.loads(DATA.read_text());x=json.loads(X.read_text());m=json.loads(MAP.read_text());c=json.loads(CYL.read_text());dot=json.loads(DOTTED.read_text())
 if d["sha256"]!=sha({k:v for k,v in d.items() if k!="sha256"}):raise AssertionError("dotted atlas SHA changed")
 for k,v in {"x_m1_complete_framed_cancellation_image_sha256":x["sha256"],"yz_dotted_passage_replacement_map_sha256":m["sha256"],"yz_mapping_cylinders_verification_sha256":c["sha256"],"actual_dotted_s3_passage_cells_sha256":dot["sha256"]}.items():
  if d[k]!=v:raise AssertionError("dotted atlas source changed")
 expected={"m_2":(14445,15061),"m_3":(65370,69114),"r_xy":(94,102),"r_yz":(4,4),"r_zx":(94,102)}
 if {i["component"]:(i["atlas_core_segments"],i["atlas_push_segments"]) for i in d["framed_components"]}!=expected:raise AssertionError("dotted atlas component counts changed")
 if (d["component_count"],d["framed_core_segment_count"],d["framed_push_segment_count"],d["dotted_polygon_segment_count"],d["passage_mapping_cylinder_tetrahedra"])!=(7,80007,84383,8,21540):raise AssertionError("dotted atlas totals changed")
 if c["verdict"]!="PASS_ALL_YZ_FRAMED_PASSAGE_MAPPING_CYLINDERS_FULL" or not c["full_verifier_result"]["continuous_dotted_conversion_in_atlas"]:raise AssertionError("dotted conversion continuity missing")
 if d["completion_status"]!="COMPLETE_SEVEN_COMPONENT_FRAMED_DOTTED_ATLAS_CONSTRUCTED" or d["single_affine_s3_chart_status"]!="OPEN":raise AssertionError("dotted atlas scope changed")
 return {"verdict":"PASS_COMPLETE_SEVEN_COMPONENT_FRAMED_DOTTED_ATLAS","components":7,"framed_core_segments":80007,"framed_push_segments":84383,"dotted_segments":8,"single_affine_s3_chart_status":"OPEN","complete_pd_status":d["complete_pd_status"]}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
