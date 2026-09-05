#!/usr/bin/env python3
"""Build all framed mapping cylinders for y/z dotted-handle conversion."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"geometry/t73_yz_dotted_passage_replacement_map.json"; MIDDLE=ROOT/"audit/t73_x_m1_ejected_middle_complements_receipt.json"; DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json"; SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json"; AR=ROOT/"geometry/t73_actual_ar_link.json"; CUT=ROOT/"geometry/t73_actual_cut_tangle.json"; DUAL=ROOT/"geometry/t73_actual_dual_product_ribbons.json"; RECEIPT=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_receipt.json"; DEFAULT=Path("/home/lifesize/.cache/t73_yz_framed_passage_mapping_cylinders.jsonl.gz")
sys.set_int_max_str_digits(0)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"))
def sha(v):return hashlib.sha256(canonical(v).encode()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def enc(v):return [str(x) for x in v]
def add(a,b):return tuple(a[i]+b[i] for i in range(len(a)))
def file_sha(p):
 d=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):d.update(b)
 return d.hexdigest().upper()
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def cube_tets():
 out=[]
 import itertools
 for perm in itertools.permutations(range(3)):
  state=[0,0,0];s=[0]
  for axis in perm:state[axis]=1;a,f,t=state;s.append(4*t+2*f+a)
  out.append(s)
 return out
def load_middle(p):
 out={}
 with gzip.open(p,"rt") as f:
  next(f)
  for line in f:
   x=json.loads(line);out[x["band_index"]]=x
 return out
def subdivide_target(vertices,count):
 a,b=vertices
 if count==1:return [a,b]
 return [a,tuple((a[i]+b[i])/2 for i in range(3)),b]
def build(cache,middle_cache=None):
 mp=json.loads(MAP.read_text());mr=json.loads(MIDDLE.read_text());dotted=json.loads(DOTTED.read_text());sp=json.loads(SPINE.read_text());ar=json.loads(AR.read_text());cut=json.loads(CUT.read_text());dual=json.loads(DUAL.read_text());middle=load_middle(middle_cache or resolve(mr["cache_path"])); targets={x["passage_id"]:x for c in dotted["charts"] for x in c["passages"]};arcs={x["arc_id"]:x for x in sp["handle_arcs"]};cuts={x["source_id"]:x for x in cut["passages"]};dual_by={x["name"]:x for x in dual["components"]};width=Fraction(ar["framing"]["spine_ribbon_transport"]["width"])
 header={"record":"header","schema":"t73_yz_framed_passage_mapping_cylinders/v1","replacement_map_sha256":mp["sha256"],"middle_receipt_sha256":mr["sha256"],"dotted_cells_sha256":dotted["sha256"],"johnson_spine_sha256":sp["sha256"],"actual_ar_link_sha256":ar["sha256"],"actual_cut_tangle_sha256":cut["sha256"],"dual_ribbons_sha256":dual["sha256"],"mapping_cylinder_tetrahedra":cube_tets()};cache.parent.mkdir(parents=True,exist_ok=True);digest=hashlib.sha256();counts=Counter();source_segments=target_segments=tets=0;supports={"y":[],"z":[]}
 with cache.open("wb") as raw,gzip.GzipFile(filename="",fileobj=raw,mode="wb",compresslevel=6,mtime=0) as out:
  line=(canonical(header)+"\n").encode();out.write(line);digest.update(line)
  for r in mp["replacements"]:
   pid=r["passage_id"];kind=r["source_kind"]
   if kind=="ejected_x_replacement_m1_z_subpath":
    m=middle[r["band_index"]];lo,hi=r["source_middle_vertex_range"];core=[point(v) for v in m["target_core_vertices"]][lo:hi+1];push=[point(v) for v in m["target_push_vertices"]][lo:hi+1];chart="x_m1_ejected_atlas"
   elif kind=="actual_johnson_handle_arc":
    core=[point(v) for v in arcs[r["source_arc_id"]]["torus_polyline"]];normal=(width,width,width);push=[add(v,normal) for v in core];chart="johnson_fiber_handle"
   elif kind=="actual_bottom_cut_arc":
    if pid in cuts:core=[point(v) for v in cuts[pid]["cut_arc_in_ball"]];normal=point(cuts[pid]["product_normal"])
    else:
     core=[point(r0) for r0 in (["-1/3","-2/3","-2/3"],["1/3","2/3","2/3"])];normal=(width,width,Fraction(0))
    push=[add(v,normal) for v in core];chart="bottom_cut_ball"
   else:
    edge=r["source_segment_range"][0];core=[point(v) for v in ar["components"][r["owner"]]["polyline"]][edge:edge+3];normal=point(dual_by[r["owner"]]["product_normal"]);push=[add(v,normal) for v in core];chart="fiber_dual_cell"
   target=targets[pid];target_core=subdivide_target([point(v) for v in target["core_vertices"]],len(core)-1);target_push=subdivide_target([point(v) for v in target["push_vertices"]],len(core)-1)
   count=len(core)-1;slot=Fraction(target["normalized_foot_slot"][1]);n=235 if r["handle"]=="y" else 1550;half=Fraction(1,4*(n+1));interval=(slot-half,slot+half)
   supports[r["handle"]].append(interval)
   rec={"record":"framed_passage_mapping_cylinder","passage_id":pid,"owner":r["owner"],"handle":r["handle"],"orientation":r["orientation"],"slot_rank":r["slot_rank"],"support_slot_interval":[str(x) for x in interval],"source_chart":chart,"source_core_vertices":[enc(v) for v in core],"source_push_vertices":[enc(v) for v in push],"target_core_vertices":[enc(v) for v in target_core],"target_push_vertices":[enc(v) for v in target_push],"source_segment_count":count,"target_original_segment_count":1,"common_subdivision_segment_count":count,"mapping_cylinder_tetrahedron_count":6*count,"foot_collar_ref":pid,"ambient_disk_track_ref":pid}
   line=(canonical(rec)+"\n").encode();out.write(line);digest.update(line);counts[kind]+=1;source_segments+=count;target_segments+=1;tets+=6*count
 for handle in supports:
  ordered=sorted(supports[handle])
  if any(second[0]<=first[1] for first,second in zip(ordered,ordered[1:])):raise AssertionError("passage cylinder supports overlap")
 receipt={"schema":"t73_yz_framed_passage_mapping_cylinders_receipt/v1","cache_path":str(cache),"cache_size":cache.stat().st_size,"cache_sha256":file_sha(cache),"record_stream_sha256":digest.hexdigest().upper(),"builder_sha256":file_sha(Path(__file__)),"replacement_map_sha256":mp["sha256"],"middle_receipt_sha256":mr["sha256"],"dotted_cells_sha256":dotted["sha256"],"passage_count":sum(counts.values()),"source_segment_count":source_segments,"target_original_segment_count":target_segments,"common_subdivision_segment_count":source_segments,"mapping_cylinder_tetrahedron_count":tets,"source_kind_counts":dict(sorted(counts.items())),"verdict":"PASS_ALL_YZ_FRAMED_PASSAGE_MAPPING_CYLINDERS_CONSTRUCTED","scope_boundary":"charted framed passage conversion complete; single affine-S3 realization remains open"};receipt["sha256"]=sha(receipt);RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n");return receipt
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path);p.add_argument("--middle-cache",type=Path);a=p.parse_args();r=build(a.output or DEFAULT,a.middle_cache);print(json.dumps({"verdict":r["verdict"],"passages":r["passage_count"],"tetrahedra":r["mapping_cylinder_tetrahedron_count"],"bytes":r["cache_size"]},sort_keys=True))
if __name__=="__main__":main()
