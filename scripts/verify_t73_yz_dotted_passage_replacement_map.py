#!/usr/bin/env python3
"""Independently verify all 1785 y/z passage replacement bindings."""
from __future__ import annotations
import gzip, hashlib, json
from collections import Counter
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA=ROOT/"geometry/t73_yz_dotted_passage_replacement_map.json"; CYCLES=ROOT/"geometry/t73_final_component_passage_cycles.json"; FOLIATION=ROOT/"geometry/t73_x_m1_parallel_foliation.json"; MIDDLE=ROOT/"audit/t73_x_m1_ejected_middle_complements_receipt.json"; DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json"; COLLARS=ROOT/"geometry/t73_dotted_s3_foot_collars.json"; AMBIENT=ROOT/"geometry/t73_dotted_disk_ambient_extensions.json"; XIMAGE=ROOT/"geometry/t73_x_m1_complete_framed_cancellation_image.json"
def canonical_sha(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def point(values): return tuple(Fraction(v) for v in values)
def resolve(value):
 p=Path(value)
 if p.exists() or len(value)<3 or value[1:3] not in (":\\",":/"): return p
 return Path("/mnt")/value[0].lower()/value[3:].replace("\\","/")
def equiv(a,b): return a[3]==b[3] and all((a[i]-b[i])/4==int((a[i]-b[i])/4) for i in range(3))
def verify():
 d=json.loads(DATA.read_text()); cycles=json.loads(CYCLES.read_text()); fol=json.loads(FOLIATION.read_text()); mr=json.loads(MIDDLE.read_text()); dotted=json.loads(DOTTED.read_text()); collars=json.loads(COLLARS.read_text()); ambient=json.loads(AMBIENT.read_text()); xi=json.loads(XIMAGE.read_text())
 if d["sha256"]!=canonical_sha({k:v for k,v in d.items() if k!="sha256"}): raise AssertionError("replacement-map payload SHA changed")
 bindings={"final_component_passage_cycles_sha256":cycles["sha256"],"m1_parallel_foliation_sha256":fol["sha256"],"ejected_middle_complements_receipt_sha256":mr["sha256"],"actual_dotted_s3_passage_cells_sha256":dotted["sha256"],"dotted_s3_foot_collars_sha256":collars["sha256"],"dotted_disk_ambient_extensions_sha256":ambient["sha256"],"x_m1_complete_framed_cancellation_image_sha256":xi["sha256"]}
 if any(d[k]!=v for k,v in bindings.items()): raise AssertionError("replacement-map source changed")
 expected=[p for c in cycles["components"] for p in c["passages"]]; target={p["passage_id"]:p for c in dotted["charts"] for p in c["passages"]}; collar_ids={x["passage_id"] for x in collars["endpoint_records"]}
 middles={}
 with gzip.open(resolve(mr["cache_path"]),"rt") as f:
  next(f)
  for line in f:
   x=json.loads(line);middles[x["band_index"]]=x
 base=[point(v) for v in fol["base_vertices"]]; normals=[point(v) for v in fol["unit_normal_field"]]; kinds=Counter(); source=target_count=xcount=0
 for p,r in zip(expected,d["replacements"]):
  if r["passage_id"]!=p["passage_id"] or r["owner"]!=p["component"] or r["orientation"]!=p["orientation"] or r["passage_id"] not in target or r["passage_id"] not in collar_ids or r["dotted_passage_sha256"]!=canonical_sha(target[r["passage_id"]]): raise AssertionError("replacement provenance changed")
  kinds[r["source_kind"]]+=1; source+=r["source_core_segment_count"];target_count+=1
  if r["source_kind"]=="ejected_x_replacement_m1_z_subpath":
   xcount+=1;m=middles[r["band_index"]];level=Fraction(m["parallel_level"]);values=[point(v) for v in m["source_core_vertices"]];order=[18,19,20] if r["orientation"]==1 else [20,19,18];indices=[]
   for i in order:
    q=tuple(base[i][a]+level*normals[i][a] for a in range(4));hits=[j for j,v in enumerate(values) if equiv(v,q)]
    if len(hits)!=1:raise AssertionError("x replacement z-subpath lost")
    indices+=hits
   if r["source_base_vertex_order"]!=order or r["source_middle_vertex_range"]!=[indices[0],indices[-1]] or indices!=list(range(indices[0],indices[0]+3)):raise AssertionError("x replacement range changed")
 expected_kinds={"ejected_x_replacement_m1_z_subpath":1513,"actual_johnson_handle_arc":262,"actual_mapping_torus_bottom_closure":2,"actual_dual_two_segment_passage":8}
 if dict(kinds)!=expected_kinds or (len(d["replacements"]),xcount,source,target_count)!=(1785,1513,3590,1785):raise AssertionError("replacement inventory changed")
 if (d["post_conversion_core_segment_count"],d["post_conversion_push_segment_count"])!=(80007,84383):raise AssertionError("post-conversion totals changed")
 return {"verdict":"PASS_ALL_YZ_PASSAGES_BOUND_TO_DOTTED_S3_REPLACEMENTS","replacements":1785,"x_replacements":1513,"source_core_segments":3590,"target_core_segments":1785,"post_conversion_core_segments":80007,"post_conversion_push_segments":84383,"mapping_cylinder_status":d["mapping_cylinder_status"]}
if __name__=="__main__":print(json.dumps(verify(),sort_keys=True))
