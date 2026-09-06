#!/usr/bin/env python3
"""Verify one exact pairwise core-linking SQLite ledger."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3,sys
from fractions import Fraction
from pathlib import Path
from export_t73_full_handle_diagram import add_scaled,det2,dot,projected_intersection,projection,sub
ROOT=Path(__file__).resolve().parents[1];BUILDER=ROOT/"scripts/build_t73_pairwise_core_linking.py";CORE=ROOT/"geometry/t73_affine_s3_core_realization.json";CORE_VERIFY=ROOT/"audit/t73_affine_s3_core_realization_verification.json";ORDER=("m_2","m_3","r_xy","r_yz","r_zx")
def slug(a,b):return f"{a.replace('_','')}_{b.replace('_','')}"
def rp(a,b):return ROOT/f"audit/t73_pairwise_core_linking_{slug(a,b)}_receipt.json"
def cs(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest().upper()
def fs(p):
 d=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(8*1024*1024),b""):d.update(x)
 return d.hexdigest().upper()
def point(v):return tuple(Fraction(x) for x in v)
def resolve(v):
 p=Path(v)
 if p.exists() or len(v)<3 or v[1:3] not in (":\\",":/"):return p
 return Path("/mnt")/v[0].lower()/v[3:].replace("\\","/")
def check_receipt(a,b):
 r=json.loads(rp(a,b).read_text());c=json.loads(CORE.read_text());v=json.loads(CORE_VERIFY.read_text());checks={"payload":r["sha256"]==cs({k:x for k,x in r.items() if k!="sha256"}),"builder":r["builder_sha256"]==fs(BUILDER),"sources":r["affine_core_sha256"]==c["sha256"] and r["affine_core_verification_sha256"]==v["sha256"],"pair":r["first_component"]==a and r["second_component"]==b,"parity":r["signed_sum"]%2==0 and r["integer_linking"]==r["signed_sum"]//2,"verdict":r["verdict"]=="PASS_EXACT_PAIRWISE_CORE_LINKING"}
 if not all(checks.values()):raise AssertionError(f"pairwise receipt failed: {checks}")
 return r,checks
def verify_database(a,b,full=False,check_database_sha=False):
 r,checks=check_receipt(a,b);db=resolve(r["database_path"])
 if not db.is_file() or db.stat().st_size!=r["database_size"]:raise AssertionError("pairwise database missing/size changed")
 if check_database_sha and fs(db)!=r["database_sha256"]:raise AssertionError("pairwise database SHA changed")
 con=sqlite3.connect(f"file:{db}?mode=ro",uri=True)
 if con.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise AssertionError("pairwise SQLite integrity failed")
 agg=con.execute("SELECT COUNT(*),COALESCE(SUM(sign),0),COALESCE(SUM(over_component=?),0),MIN(id),MAX(id) FROM crossings",(a,)).fetchone()
 if agg!=(r["crossing_count"],r["signed_sum"],r["first_over_crossing_count"],0,r["crossing_count"]-1):raise AssertionError("pairwise aggregate changed")
 exact=0
 if full:
  c=json.loads(CORE.read_text());curves={x["component"]:[point(v) for v in x["vertices"]] for x in c["framed_core_components"]};first,second=curves[a],curves[b];basis=tuple(tuple(Fraction(x) for x in row) for row in r["projection_basis"]);height=tuple(Fraction(x) for x in r["height_covector"])
  for row_id,i,j,phash,over,sign in con.execute("SELECT id,first_segment,second_segment,projection_point_sha256,over_component,sign FROM crossings ORDER BY id"):
   hit=projected_intersection(first[i],first[i+1],second[j],second[j+1],basis,f"verify:{a}/{b}:{row_id}")
   if hit is None:raise AssertionError("stored pair does not cross")
   s,t,q=hit;pa=add_scaled(first[i],sub(first[i+1],first[i]),s);pb=add_scaled(second[j],sub(second[j+1],second[j]),t);ha,hb=dot(height,pa),dot(height,pb);expected_over=a if ha>hb else b;ta=sub(projection(first[i+1],basis),projection(first[i],basis));tb=sub(projection(second[j+1],basis),projection(second[j],basis));det=det2(ta,tb) if expected_over==a else det2(tb,ta);expected_sign=1 if det>0 else -1
   if ha==hb or not det or phash!=cs([str(q[0]),str(q[1])]) or over!=expected_over or sign!=expected_sign:raise AssertionError(f"pairwise crossing changed at {row_id}")
   exact+=1
   if exact%500000==0:print(f"{a}/{b}: verified {exact}/{r['crossing_count']}",file=sys.stderr,flush=True)
 con.close();return {"verdict":"PASS_PAIRWISE_CORE_LINKING_FULL" if full else "PASS_PAIRWISE_CORE_LINKING_DATABASE_INTEGRITY_ONLY","first":a,"second":b,"fast_checks":checks,"crossings":r["crossing_count"],"signed_sum":r["signed_sum"],"integer_linking":r["integer_linking"],"exact_crossings_recomputed":exact,"database_sha_checked":check_database_sha}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("first",choices=ORDER);p.add_argument("second",choices=ORDER);p.add_argument("--full",action="store_true");p.add_argument("--database",action="store_true");p.add_argument("--check-database-sha",action="store_true");x=p.parse_args();print(json.dumps(verify_database(x.first,x.second,x.full,x.check_database_sha) if x.full or x.database else {"verdict":"PASS_PAIRWISE_CORE_LINKING_RECEIPT","checks":check_receipt(x.first,x.second)[1]},sort_keys=True))
