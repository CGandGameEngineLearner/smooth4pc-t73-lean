# T73 topology toolchain and proof boundary

## Regina baseline

The reproducible third-party topology baseline is
[Regina](https://regina-normal.github.io/), whose Python engine recognises
3-manifold handlebodies and manipulates triangulations.  The repository keeps
the virtual environment outside the Git worktree:

```bash
python3 -m venv ~/.venvs/t73-topology
~/.venvs/t73-topology/bin/python -m pip install --upgrade pip 'regina>=7.4'
~/.venvs/t73-topology/bin/python \
  scripts/verify_t73_handlebody_bridge_regina.py --write --check
```

`scripts/verify_t73_handlebody_bridge_regina.py` imports the stored face
gluings for the four Johnson/AR dual-block handlebodies, asks Regina to
recognise each one, and rejects a deliberately malformed gluing.  This is an
independent check of the genus-three handlebody substrate of P0a; it does not
replace the Johnson--AR ambient argument.

## What this toolchain can and cannot close

Regina is appropriate for a future `t73_gs1_gp3_witness/v1`: it can check the
explicit triangulated closed boundary, the embedded normal sphere subcomplexes
and the replayed cut-and-cap surgery trace.  The gate
`scripts/verify_t73_gs1_gp3.py` remains fail-closed until that witness contains
the actual post-two-handle boundary, detector subcomplex, three sphere
neighbourhoods, and final recognised three-sphere.

SnapPy/Spherogram can independently parse a complete standard PD presentation
and compare a link exterior, while Regina can consume the resulting
triangulation.  They cannot infer missing Kirby bands, dotted-circle data,
integer framings, or a relative AR-to-selected-source map.  Likewise, a link
homology calculator can check finite Khovanov complexes but does not construct
the MWW coend/currying maps or four-dimensional foam functoriality required by
C and S.

The current 20-ribbon Gmsh frame is a verified tetrahedral model of a selected
source prefix.  It is not a triangulation of the actual post-two-handle
boundary and has no source-to-target map; it must not be passed to the S gate
as a substitute for a `t73_gs1_gp3_witness/v1` witness.
