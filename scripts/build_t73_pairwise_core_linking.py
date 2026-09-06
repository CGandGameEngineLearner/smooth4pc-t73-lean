#!/usr/bin/env python3
"""Build an exact crossing ledger and linking number for two affine core components."""
from __future__ import annotations
import argparse,hashlib,json,math,sqlite3,sys
from fractions import Fraction
from pathlib import Path
from shapely.geometry import box
from shapely.strtree import STRtree
from export_t73_full_handle_diagram import add_scaled,det2,dot,projected_intersection,projection,sub
ROOT=Path(__file__).resolve().parents[1];CORE=ROOT/"geometry/t73_affine_s3_core_realization.json";VERIFY=ROOT/"audit/t73_affine_s3_core_realization_verification.json"
Q=1000033;BASIS=((Fraction(1),Fraction(1),Fraction(1,Q)),(Fraction(1,Q**2),Fraction(0),Fraction(1)));HEIGHT=(Fraction(1),Fraction(1,Q**3)-1,Fraction(-1,Q**2));ORDER=("m_2","m_3","r_xy","r_yz","r_zx")
def point(v):return tuple(Fraction(x) for x in v)
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def fs(p):
 d=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):d.update(b)
 return d.hexdigest().upper()
def boxes(v):
 out=[]
 for a,b in zip(v,v[1:]):
  p,q=projection(a,BASIS),projection(b,BASIS)
  if p==q:raise AssertionError("pairwise projection collapses segment")
  out.append(box(math.nextafter(float(min(p[0],q[0])),-math.inf),math.nextafter(float(min(p[1],q[1])),-math.inf),math.nextafter(float(max(p[0],q[0])),math.inf),math.nextafter(float(max(p[1],q[1])),math.inf)))
 return out
def slug(a,b):return f"{a.replace('_','')}_{b.replace('_','')}"
def build(first,second,database):
 if ORDER.index(first)>=ORDER.index(second):raise AssertionError("pair order must follow canonical component order")
 core=json.loads(CORE.read_text());verification=json.loads(VERIFY.read_text());curves={c["component"]:[point(v) for v in c["vertices"]] for c in core["framed_core_components"]};a,b=curves[first],curves[second]
 if database.exists():database.unlink()
 database.parent.mkdir(parents=True,exist_ok=True);con=sqlite3.connect(database);con.executescript("PRAGMA journal_mode=OFF;PRAGMA synchronous=OFF;CREATE TABLE crossings(id INTEGER PRIMARY KEY,first_segment INTEGER,second_segment INTEGER,projection_point_sha256 TEXT UNIQUE,over_component TEXT,sign INTEGER);CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);")
 ab,bb=boxes(a),boxes(b);tree=STRtree(bb);broad=count=signed=first_over=0;batch=[]
 for i,box_i in enumerate(ab):
  if i%500==0:print(f"{first}/{second}: {i}/{len(ab)} crossings={count}",file=sys.stderr,flush=True)
  for raw in tree.query(box_i):
   j=int(raw);broad+=1;hit=projected_intersection(a[i],a[i+1],b[j],b[j+1],BASIS,f"{first}/{second}:{i}/{j}")
   if hit is None:continue
   s,t,q=hit;pa=add_scaled(a[i],sub(a[i+1],a[i]),s);pb=add_scaled(b[j],sub(b[j+1],b[j]),t);ha,hb=dot(HEIGHT,pa),dot(HEIGHT,pb)
   if ha==hb:raise AssertionError("pairwise core components intersect")
   ta=sub(projection(a[i+1],BASIS),projection(a[i],BASIS));tb=sub(projection(b[j+1],BASIS),projection(b[j],BASIS));over=first if ha>hb else second;det=det2(ta,tb) if over==first else det2(tb,ta)
   if not det:raise AssertionError("pairwise crossing nontransverse")
   sign=1 if det>0 else -1;batch.append((count,i,j,cs([str(q[0]),str(q[1])]),over,sign));count+=1;signed+=sign;first_over+=over==first
   if len(batch)>=5000:con.executemany("INSERT INTO crossings VALUES(?,?,?,?,?,?)",batch);con.commit();batch=[]
 if batch:con.executemany("INSERT INTO crossings VALUES(?,?,?,?,?,?)",batch)
 con.commit();con.close()
 if signed%2:raise AssertionError("pairwise mixed crossing sum is odd")
 receipt={"schema":"t73_pairwise_core_linking/v1","first_component":first,"second_component":second,"database_path":str(database),"database_size":database.stat().st_size,"database_sha256":fs(database),"builder_sha256":fs(Path(__file__)),"affine_core_sha256":core["sha256"],"affine_core_verification_sha256":verification["sha256"],"projection_basis":[[str(x) for x in r] for r in BASIS],"height_covector":[str(x) for x in HEIGHT],"first_segment_count":len(a)-1,"second_segment_count":len(b)-1,"broad_candidate_count":broad,"crossing_count":count,"first_over_crossing_count":first_over,"signed_sum":signed,"integer_linking":signed//2,"verdict":"PASS_EXACT_PAIRWISE_CORE_LINKING"};receipt["sha256"]=cs(receipt);out=ROOT/f"audit/t73_pairwise_core_linking_{slug(first,second)}_receipt.json";out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n");return receipt
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("first",choices=ORDER);p.add_argument("second",choices=ORDER);p.add_argument("--database",type=Path);x=p.parse_args();db=x.database or Path.home()/f".cache/t73_pairwise_core_linking_{slug(x.first,x.second)}.sqlite";print(json.dumps(build(x.first,x.second,db),sort_keys=True))
