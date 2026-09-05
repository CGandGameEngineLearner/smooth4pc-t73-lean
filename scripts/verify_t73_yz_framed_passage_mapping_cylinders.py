#!/usr/bin/env python3
"""Verify all framed y/z dotted-passage mapping cylinders."""
from __future__ import annotations
import argparse,gzip,hashlib,json
from collections import Counter
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/"audit/t73_yz_framed_passage_mapping_cylinders_receipt.json";BUILDER=ROOT/"scripts/build_t73_yz_framed_passage_mapping_cylinders.py";MAP=ROOT/"geometry/t73_yz_dotted_passage_replacement_map.json";MIDDLE=ROOT/"audit/t73_x_m1_ejected_middle_complements_receipt.json";DOTTED=ROOT/"geometry/t73_actual_dotted_s3_passage_cells.json";SPINE=ROOT/"geometry/t73_johnson_spine_embedding.json";AR=ROOT/"geometry/t73_actual_ar_link.json";CUT=ROOT/"geometry/t73_actual_cut_tangle.json";DUAL=ROOT/"geometry/t73_actual_dual_product_ribbons.json"
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
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
def subdivide(v,n):
 a,b=v
 return [tuple(a[i]+Fraction(k,n)*(b[i]-a[i]) for i in range(3)) for k in range(n+1)]
def bottom_closure(ar,spine,name):
 core=[point(v) for v in ar["components"][name]["core_polyline_T3xI"]];idx={"m_2":1,"m_3":2}[name];spoke=spine["components"][idx]["spoke"];plus=point(spoke["stage_plus"])+(Fraction(1),);minus=point(spoke["stage_minus"])+(Fraction(1),);i=core.index(plus);j=core.index(minus);path=core[j:]+core[1:i+1]
 if len(path)-1!=12:raise AssertionError("bottom closure count changed")
 return path
def check_receipt():
 r=json.loads(RECEIPT.read_text());mp=json.loads(MAP.read_text());mr=json.loads(MIDDLE.read_text());d=json.loads(DOTTED.read_text())
 checks={"payload":r["sha256"]==sha({k:v for k,v in r.items() if k!="sha256"}),"builder":r["builder_sha256"]==file_sha(BUILDER),"sources":r["replacement_map_sha256"]==mp["sha256"] and r["middle_receipt_sha256"]==mr["sha256"] and r["dotted_cells_sha256"]==d["sha256"],"counts":r["passage_count"]==1785 and r["source_segment_count"]==3590 and r["target_original_segment_count"]==1785 and r["mapping_cylinder_tetrahedron_count"]==21540,"verdict":r["verdict"]=="PASS_ALL_YZ_FRAMED_PASSAGE_MAPPING_CYLINDERS_CONSTRUCTED"}
 if not all(checks.values()):raise AssertionError(f"yz cylinder receipt failed: {checks}")
 return r,checks
def verify_full(middle_cache=None,check_cache_sha=False):
 receipt,checks=check_receipt();mp=json.loads(MAP.read_text());mr=json.loads(MIDDLE.read_text());dotted=json.loads(DOTTED.read_text());sp=json.loads(SPINE.read_text());ar=json.loads(AR.read_text());cut=json.loads(CUT.read_text());dual=json.loads(DUAL.read_text());targets={x["passage_id"]:x for c in dotted["charts"] for x in c["passages"]};arcs={x["arc_id"]:x for x in sp["handle_arcs"]};cuts={x["source_id"]:x for x in cut["passages"]};dual_by={x["name"]:x for x in dual["components"]};width=Fraction(ar["framing"]["spine_ribbon_transport"]["width"])
 middles={}
 with gzip.open(middle_cache or resolve(mr["cache_path"]),"rt") as f:
  next(f)
  for line in f:
   x=json.loads(line);middles[x["band_index"]]=x
 cache=resolve(receipt["cache_path"])
 if check_cache_sha and file_sha(cache)!=receipt["cache_sha256"]:raise AssertionError("yz cylinder cache SHA changed")
 supports={"y":[],"z":[]};kinds=Counter();segments=tets=push_checks=0
 with gzip.open(cache,"rt") as f:
  header=json.loads(next(f));records=[json.loads(line) for line in f]
 if len(header["mapping_cylinder_tetrahedra"])!=6 or len(records)!=1785:raise AssertionError("yz cylinder cache structure changed")
 for source,r in zip(mp["replacements"],records):
  pid=source["passage_id"];kind=source["source_kind"]
  if r["passage_id"]!=pid or r["owner"]!=source["owner"] or r["orientation"]!=source["orientation"]:raise AssertionError("yz cylinder provenance changed")
  if kind=="ejected_x_replacement_m1_z_subpath":
   m=middles[source["band_index"]];lo,hi=source["source_middle_vertex_range"];core=[point(v) for v in m["target_core_vertices"]][lo:hi+1];push=[point(v) for v in m["target_push_vertices"]][lo:hi+1]
  elif kind=="actual_johnson_handle_arc":
   core=[point(v) for v in arcs[source["source_arc_id"]]["torus_polyline"]];push=[add(v,(width,width,width)) for v in core]
  elif kind=="actual_mapping_torus_bottom_closure":
   core=bottom_closure(ar,sp,source["owner"]);normal=(width,width,width,Fraction(0))
   push=[add(v,normal) for v in core]
  else:
   edge=source["source_segment_range"][0];core=[point(v) for v in ar["components"][source["owner"]]["polyline"]][edge:edge+3];normal=point(dual_by[source["owner"]]["product_normal"]);push=[add(v,normal) for v in core]
  target=targets[pid];tc=subdivide([point(v) for v in target["core_vertices"]],len(core)-1);tp=subdivide([point(v) for v in target["push_vertices"]],len(core)-1)
  if [point(v) for v in r["source_core_vertices"]]!=core or [point(v) for v in r["source_push_vertices"]]!=push or [point(v) for v in r["target_core_vertices"]]!=tc or [point(v) for v in r["target_push_vertices"]]!=tp:raise AssertionError("yz framed cylinder boundary changed")
  if any(a==b for a,b in zip(core,push)) or any(a==b for a,b in zip(tc,tp)):raise AssertionError("yz framing collapsed")
  interval=tuple(map(Fraction,r["support_slot_interval"]));supports[r["handle"]].append(interval);count=len(core)-1
  if r["mapping_cylinder_tetrahedron_count"]!=6*count:raise AssertionError("yz cylinder tetra count changed")
  kinds[kind]+=1;segments+=count;tets+=6*count;push_checks+=len(core)+len(tc)
 for h in supports:
  q=sorted(supports[h])
  if any(b[0]<=a[1] for a,b in zip(q,q[1:])):raise AssertionError("yz cylinder supports overlap")
 if segments!=3590 or tets!=21540 or dict(kinds)!=receipt["source_kind_counts"]:raise AssertionError("yz cylinder full totals changed")
 return {"verdict":"PASS_ALL_YZ_FRAMED_PASSAGE_MAPPING_CYLINDERS_FULL","fast_checks":checks,"passages":1785,"source_segments":segments,"mapping_cylinder_tetrahedra":tets,"framing_vertex_checks":push_checks,"disjoint_support_checks":1783,"cache_sha_checked":check_cache_sha,"continuous_dotted_conversion_in_atlas":True,"single_affine_s3_chart_status":"OPEN"}
def main():
 p=argparse.ArgumentParser();p.add_argument("--full",action="store_true");p.add_argument("--middle-cache",type=Path);p.add_argument("--check-cache-sha",action="store_true");a=p.parse_args();r=verify_full(a.middle_cache,a.check_cache_sha) if a.full else {"verdict":"PASS_YZ_PASSAGE_CYLINDER_RECEIPT","checks":check_receipt()[1],"passages":1785};print(json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
