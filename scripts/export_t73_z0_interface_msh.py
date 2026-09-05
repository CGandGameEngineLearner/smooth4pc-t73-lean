#!/usr/bin/env python3
"""Export the fixed rational z=0 interface as a discrete Gmsh surface mesh."""
from __future__ import annotations
import argparse, json
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'geometry/t73_z0_interface_triangulation.json'

def export(output: Path | None = None):
    import gmsh
    data=json.loads(INPUT.read_text(encoding='utf-8'))
    vertices=[tuple(Fraction(x) for x in row) for row in data['vertices']]
    triangles=data['triangles']
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal',0)
        gmsh.model.add('t73-z0-interface')
        surface=gmsh.model.addDiscreteEntity(2,1)
        tags=list(range(1,len(vertices)+1))
        coordinates=[float(value) for point in vertices for value in point]
        gmsh.model.mesh.addNodes(2,surface,tags,coordinates)
        gmsh.model.mesh.addElements(2,surface,[2],[list(range(1,len(triangles)+1))],[[vertex+1 for tri in triangles for vertex in tri]])
        node_tags, coords, _ = gmsh.model.mesh.getNodes(2,surface,includeBoundary=True)
        kinds, _tags, rows=gmsh.model.mesh.getElements(2,surface)
        if list(node_tags)!=tags or kinds!=[2] or len(rows)!=1 or len(rows[0])!=3*len(triangles):
            raise AssertionError('Gmsh did not retain the interface simplex set')
        if output: gmsh.write(str(output))
        return {'vertices':len(vertices),'triangles':len(triangles),'surface_entity':surface}
    finally:
        gmsh.finalize()

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path); a=p.parse_args()
    r=export(a.output); print(f"T73_Z0_INTERFACE_MSH=PASS vertices={r['vertices']} triangles={r['triangles']}")
if __name__=='__main__': main()
