# Chosen area-basis 3-handle slide receipt

Date: 2026-08-30  
Scope: topology of the 3-handle attaching-sphere system relative to the old
coefficient link.  No chain-level naturality is claimed.

## Matrix gate

The coefficient matrix, with columns `K1,K2,C3`, is

```text
V = [  0   1   0
      40  10  11
     189  80  52 ].
```

Direct computation gives

```text
det(V) = -1,
V^-1 = [  360   52  -11
             1    0    0
         -1310 -189   40 ].
```

For the original `D` columns,

```text
D V = [  189    79    53
        -1201  -502  -337
          189    79    52 ].
```

Thus the chosen spherical classes are

```text
K1 = (189,-1201,189),
K2 = (79,-502,79),
C3 = (53,-337,52).
```

The r-only obstruction row becomes `(0,0,1)`.

## Original basis to chosen basis

At every line, slot numbers refer to the **current** ordered sphere system.
`add source -> moving (k)` means `|k|` slides of the moving sphere over the
source sphere, with sign `sign(k)`.

```text
 1. add 3 -> 1 (+80)   source=3, moving=1, repeats=80
 2. add 2 -> 1 (+10)   source=2, moving=1, repeats=10
 3. add 3 -> 2 ( +5)   source=3, moving=2, repeats=5
 4. neg 3              reverse orientation/coorientation of slot 3
 5. add 2 -> 3 ( +3)   source=2, moving=3, repeats=3
 6. swap 2,3
 7. add 2 -> 3 ( +1)   source=2, moving=3, repeats=1
 8. swap 2,3
 9. add 2 -> 3 ( +1)   source=2, moving=3, repeats=1
10. swap 2,3
11. add 2 -> 3 ( +1)   source=2, moving=3, repeats=1
12. swap 2,3
13. add 2 -> 3 ( +3)   source=2, moving=3, repeats=3
14. swap 2,3
15. swap 1,2
```

Totals:

```text
add macros:                 8
slot swaps:                 6
orientation reversals:      1
expanded signed slides:    104
all elementary events:     111
```

The JSON records the coefficient columns and `D` columns after every macro and
replays the complete list from `I` to `V` exactly.

## Relative support

Let `L_old` be the finite old coefficient link.  Each attaching sphere is
disjoint from `L_old`.  For one sphere slide, choose the slide arc in the
complement of `L_old`; a generic arc can be perturbed off a finite 1-manifold
in a 3-manifold.  The band support is contained in a neighborhood of the two
spheres and this arc.

For repeated slides, take finitely many parallel copies of the relative arc in
its normal 2-disk.  These supports remain disjoint from a fixed neighborhood
of `L_old`.  Swaps are relabelings of handles, and the orientation reversal is
supported in the attaching-sphere parameterization.  Consequently every step
is the pointwise identity near `L_old`.

This proves a topological 3-handle slide equivalence relative to the old link.
It does not prove that any external chain functional is natural under these
slides.

## Verdict

```text
integer replay:                         PASS
unimodular basis:                       PASS, det=-1
topological 3-handle slides:            PASS relative old link
expanded slide weight:                  104
chain-level slide naturality:           NOT CLAIMED
```

Reproduction:

```powershell
python -B D:\tmp\r6\agents\unimodular_easy_spheres\area_basis_3handle_slide_receipt.py --write
```
