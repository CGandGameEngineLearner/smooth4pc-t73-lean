#!/usr/bin/env python3
"""Verify one exact product self-linking SQLite ledger and receipt."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3,sys
from fractions import Fraction
from pathlib import Path
from export_t73_full_handle_diagram import add_scaled,det2,dot,projected_intersection,projection,sub
ROOT=Path(__file__).resolve().parents[1];BUILDER=ROOT/"scripts/build_t73_product_self_linking_component.py";FRAMED=ROOT/"audit/t73_affine_s3_product_framed_realization_receipt.json";CLEARANCE=ROOT/"audit/t73_affine_s3_product_ribbon_global_clearance.json"
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def fs(p):
 d=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):d.update(b)
 return d.hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def receipt_path(component):return ROOT/f"audit/t73_product_self_linking_{component.replace('_','')}_receipt.json"
def check_receipt(component):
 r=json.loads(receipt_path(component).read_text());fr=json.loads(FRAMED.read_text());cl=json.loads(CLEARANCE.read_text());checks={"payload":r["sha256"]==cs({k:v for k,v in r.items() if k!="sha256"}),"builder":r["builder_sha256"]==fs(BUILDER),"sources":r["product_framed_receipt_sha256"]==fr["sha256"] and r["product_ribbon_clearance_sha256"]==cl["sha256"],"component":r["component"]==component,"parity":r["signed_sum"]%2==0 and r["integer_self_linking"]==r["signed_sum"]//2,"verdict":r["verdict"]=="PASS_EXACT_PRODUCT_SELF_LINKING_COMPONENT"}
 if not all(checks.values()):raise AssertionError(f"self-linking receipt failed: {checks}")
 return r,checks
def verify_database(component,full=False,check_database_sha=False):
 r,checks=check_receipt(component);db=resolve(r["database_path"])
 if not db.is_file() or db.stat().st_size!=r["database_size"]:raise AssertionError("self-linking database missing/size changed")
 if check_database_sha and fs(db)!=r["database_sha256"]:raise AssertionError("self-linking database SHA changed")
 con=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
 if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise AssertionError("self-linking SQLite integrity failed")
 agg=con.execute("SELECT COUNT(*),COALESCE(SUM(sign),0),COALESCE(SUM(over_role='core'),0),MIN(id),MAX(id) FROM crossings").fetchone()
 if agg!=(r["crossing_count"],r["signed_sum"],r["core_over_crossing_count"],0,r["crossing_count"]-1):raise AssertionError("self-linking aggregate changed")
 exact=0
 if full:
  fr=json.loads(FRAMED.read_text());data=json.loads(resolve(fr["cache_path"]).read_text());core=[point(v) for v in next(c for c in data["core_components"] if c["component"]==component)["vertices"]];push=[point(v) for v in next(c for c in data["push_components"] if c["component"]==component)["vertices"]];basis=tuple(tuple(Fraction(x) for x in row) for row in r["projection_basis"]);height=tuple(Fraction(x) for x in r["height_covector"])
  for row_id,i,j,phash,over,sign in con.execute("SELECT id,core_segment,push_segment,projection_point_sha256,over_role,sign FROM crossings ORDER BY id"):
   hit=projected_intersection(core[i],core[i+1],push[j],push[j+1],basis,f"verify:{component}:{row_id}")
   if hit is None:raise AssertionError("stored self-linking pair does not cross")
   a,b,q=hit;cp=add_scaled(core[i],sub(core[i+1],core[i]),a);pp=add_scaled(push[j],sub(push[j+1],push[j]),b);ch,hh=dot(height,cp),dot(height,pp);expected_over="core" if ch>hh else "push";ct=sub(projection(core[i+1],basis),projection(core[i],basis));pt=sub(projection(push[j+1],basis),projection(push[j],basis));det=det2(ct,pt) if expected_over=="core" else det2(pt,ct);expected_sign=1 if det>0 else -1
   if ch==hh or not det or phash!=cs([str(q[0]),str(q[1])]) or over!=expected_over or sign!=expected_sign:raise AssertionError(f"self-linking crossing changed at {row_id}")
   exact+=1
   if exact%500000==0:print(f"{component}: verified {exact}/{r['crossing_count']}",file=sys.stderr,flush=True)
 con.close();verdict="PASS_PRODUCT_SELF_LINKING_COMPONENT_FULL" if full else "PASS_PRODUCT_SELF_LINKING_COMPONENT_DATABASE_INTEGRITY_ONLY"
 return {"verdict":verdict,"component":component,"fast_checks":checks,"crossings":r["crossing_count"],"signed_sum":r["signed_sum"],"integer_self_linking":r["integer_self_linking"],"exact_crossings_recomputed":exact,"database_sha_checked":check_database_sha}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("component",choices=("m_2","m_3","r_xy","r_yz","r_zx"));p.add_argument("--database",action="store_true");p.add_argument("--full",action="store_true");p.add_argument("--check-database-sha",action="store_true");a=p.parse_args();print(json.dumps(verify_database(a.component,a.full,a.check_database_sha) if a.database or a.full else {"verdict":"PASS_PRODUCT_SELF_LINKING_RECEIPT","component":a.component,"checks":check_receipt(a.component)[1]},sort_keys=True))
