#!/usr/bin/env python3
"""Build an exact core/product-push crossing ledger for one affine component."""
from __future__ import annotations
import argparse,hashlib,json,math,sqlite3,sys
from fractions import Fraction
from pathlib import Path
from shapely.geometry import box
from shapely.strtree import STRtree
from export_t73_full_handle_diagram import DiagramError,add_scaled,det2,dot,projected_intersection,projection,sub
ROOT=Path(__file__).resolve().parents[1];FRAMED=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json";CLEARANCE=ROOT/"audit/t73_affine_s3_product_ribbon_global_clearance.json"
Q=1000033;BASIS=((Fraction(1),Fraction(1),Fraction(1,Q)),(Fraction(1,Q**2),Fraction(0),Fraction(1)));HEIGHT=(Fraction(1),Fraction(1,Q**3)-1,Fraction(-1,Q**2))
def point(v):return tuple(Fraction(x) for x in v)
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def fs(p):
 d=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):d.update(b)
 return d.hexdigest().upper()
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def boxes(v):
 out=[]
 for a,b in zip(v,v[1:]):
  p=projection(a,BASIS);q=projection(b,BASIS)
  if p==q:raise AssertionError("selected self-linking projection collapses a segment")
  out.append(box(math.nextafter(float(min(p[0],q[0])),-math.inf),math.nextafter(float(min(p[1],q[1])),-math.inf),math.nextafter(float(max(p[0],q[0])),math.inf),math.nextafter(float(max(p[1],q[1])),math.inf)))
 return out
def build(component,database):
 fr=json.loads(FRAMED.read_text());cl=json.loads(CLEARANCE.read_text());data=json.loads(resolve(fr["cache_path"]).read_text());core=[point(v) for v in next(c for c in data["core_components"] if c["component"]==component)["vertices"]];push=[point(v) for v in next(c for c in data["push_components"] if c["component"]==component)["vertices"]]
 if database.exists():database.unlink()
 database.parent.mkdir(parents=True,exist_ok=True);con=sqlite3.connect(database);con.executescript("PRAGMA journal_mode=OFF;PRAGMA synchronous=OFF;CREATE TABLE crossings(id INTEGER PRIMARY KEY,core_segment INTEGER,push_segment INTEGER,projection_point_sha256 TEXT UNIQUE,over_role TEXT,sign INTEGER);CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);")
 cb=boxes(core);pb=boxes(push);tree=STRtree(pb);broad=crossings=signed=core_over=0;batch=[]
 for i,b in enumerate(cb):
  if i%500==0:print(f"{component}: {i}/{len(cb)} crossings={crossings}",file=sys.stderr,flush=True)
  for raw in tree.query(b):
   j=int(raw);broad+=1;hit=projected_intersection(core[i],core[i+1],push[j],push[j+1],BASIS,f"{component}:{i}/{j}")
   if hit is None:continue
   a,t,q=hit;cp=add_scaled(core[i],sub(core[i+1],core[i]),a);pp=add_scaled(push[j],sub(push[j+1],push[j]),t);ch=dot(HEIGHT,cp);ph=dot(HEIGHT,pp)
   if ch==ph:raise AssertionError("core meets product push")
   ct=sub(projection(core[i+1],BASIS),projection(core[i],BASIS));pt=sub(projection(push[j+1],BASIS),projection(push[j],BASIS));over="core" if ch>ph else "push";det=det2(ct,pt) if over=="core" else det2(pt,ct)
   if not det:raise AssertionError("nontransverse self-linking crossing")
   sign=1 if det>0 else -1;batch.append((crossings,i,j,cs([str(q[0]),str(q[1])]),over,sign));crossings+=1;signed+=sign;core_over+=over=="core"
   if len(batch)>=5000:con.executemany("INSERT INTO crossings VALUES(?,?,?,?,?,?)",batch);con.commit();batch=[]
 if batch:con.executemany("INSERT INTO crossings VALUES(?,?,?,?,?,?)",batch)
 meta={"component":component,"basis":[[str(x) for x in r] for r in BASIS],"height":[str(x) for x in HEIGHT],"broad":broad,"crossings":crossings,"signed_sum":signed};con.executemany("INSERT INTO metadata VALUES(?,?)",[(k,json.dumps(v,sort_keys=True)) for k,v in meta.items()]);con.commit();con.close()
 if signed%2:raise AssertionError("closed core/product push has odd crossing sum")
 receipt={"schema":"t73_product_self_linking_component/v1","component":component,"database_path":str(database),"database_size":database.stat().st_size,"database_sha256":fs(database),"builder_sha256":fs(Path(__file__)),"product_framed_receipt_sha256":fr["sha256"],"product_ribbon_clearance_sha256":cl["sha256"],"projection_basis":[[str(x) for x in r] for r in BASIS],"height_covector":[str(x) for x in HEIGHT],"core_segment_count":len(core)-1,"push_segment_count":len(push)-1,"broad_candidate_count":broad,"crossing_count":crossings,"core_over_crossing_count":core_over,"signed_sum":signed,"integer_self_linking":signed//2,"verdict":"PASS_EXACT_PRODUCT_SELF_LINKING_COMPONENT"};receipt["sha256"]=cs(receipt);out=ROOT/f"audit/t73_product_self_linking_{component.replace('_','')}_receipt.json";out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n");return receipt
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("component",choices=("m_2","m_3","r_xy","r_yz","r_zx"));p.add_argument("--database",type=Path);a=p.parse_args();db=a.database or Path.home()/f".cache/t73_product_self_linking_{a.component.replace('_','')}.sqlite";print(json.dumps(build(a.component,db),sort_keys=True))
