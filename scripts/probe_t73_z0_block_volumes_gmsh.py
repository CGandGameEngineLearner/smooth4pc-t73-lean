#!/usr/bin/env python3
"""Probe the two exact z=0 exterior blocks before embedding ribbons."""
from __future__ import annotations
import json
import argparse
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'geometry/t73_selected_source_exterior.json'
PARTITION=ROOT/'geometry/t73_selected_source_partition_z0.json'

def run(fragment_limit=1):
    import gmsh
    source=json.loads(SOURCE.read_text(encoding='utf-8'))
    partition=json.loads(PARTITION.read_text(encoding='utf-8'))
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal',0); gmsh.model.add('t73-z0-blocks'); o=gmsh.model.occ
        holes=[]
        for s in source['insertion_spheres']:
            lo=[float(x) for x in s['box_lower']]; hi=[float(x) for x in s['box_upper']]
            holes.append(o.addBox(*lo,*[hi[i]-lo[i] for i in range(3)]))
        lower=o.addBox(-20,-20,-20,40,40,20); upper=o.addBox(-20,-20,0,40,40,20)
        lo,_=o.cut([(3,lower)],[(3,h) for h in holes],removeObject=True,removeTool=False)
        hi,_=o.cut([(3,upper)],[(3,h) for h in holes],removeObject=True,removeTool=False)
        o.remove([(3,h) for h in holes],recursive=True); o.synchronize()
        # OCC fragmentation, unlike mesh.embed(), registers intersections of
        # a ribbon fragment with the hole boundary as CAD topology.
        surfaces=[]
        for item in partition['blocks']['z_nonpositive'][:fragment_limit]:
            for fragment in item['triangles']:
                points=[o.addPoint(*[float(Fraction(value)) for value in vertex]) for vertex in fragment]
                surfaces.append(o.addPlaneSurface([o.addCurveLoop([o.addLine(points[i],points[(i+1)%3]) for i in range(3)])]))
        o.fragment(lo,[(2,surface) for surface in surfaces],removeObject=True,removeTool=True)
        o.synchronize()
        volumes=[tag for _,tag in gmsh.model.getEntities(3)]
        if len(volumes)!=2: raise AssertionError('z0 block construction did not leave exactly two exterior volumes')
        gmsh.model.mesh.generate(3)
        counts=[sum(len(x) for x in gmsh.model.mesh.getElements(3,tag)[1]) for tag in volumes]
        if not all(counts): raise AssertionError('a z0 exterior block has no tetrahedra')
        return {'schema':'t73_z0_block_volume_probe/v1','source_exterior_sha256':source['sha256'],'volumes':2,'tetrahedra_by_block':counts,'occ_fragment_ribbon_surface_count':len(surfaces),'status':'PASS_FRAGMENT_BATCH_ONLY'}
    finally: gmsh.finalize()

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--fragments',type=int,default=1); a=p.parse_args()
    print(json.dumps(run(a.fragments),sort_keys=True))
