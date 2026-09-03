# Standard-sphere MWW binding for the compact presentation

**Status:** `DISCHARGED`

This note records the compact replacement for the unavailable TH1/TH2/THXY
objects.  P0 is instantiated by the Johnson certificate and C by the
Johnson-bound coefficient-comparison witness.

## Geometry relative to the detector

Under P0, the handle pattern has three 3-handles and a final 4-handle, and the
detector collar lies in a specified 3-ball `B`.  Immediately before the final
4-handle the boundary is `S3`.  Reversing the three 3-handles yields

```text
partial W2 ~= #3(S1 x S2).
```

Choose the standard complete system of three nonseparating spheres outside
`B`.  Horvat--Jablonowski Theorem 5.3 and their relative uniqueness lemma
identify it with the actual attaching system up to isotopy, permutation and
3--3 handle slides, while leaving the detector ball fixed after inessential
boundary slides are removed.

The public owner lifts and 32-step Nielsen program are optional coordinate
descriptions.  They are not needed to establish existence of the relative
standard system.

## MWW maps by local module action

Use MWW's intrinsic module-action formulation rather than decomposing a
sphere into signed bands and pivotal adapters.  At `N=2`, a 3-handle quotient
sets the one-dotted essential sphere equal to the identity and the undotted
essential sphere equal to zero.

For each sphere, removing its `b` actual two-handle core disks leaves a
connected genus-zero cobordism.  Its constant foam map is
`Delta^(b-1)`, and the core disks give `epsilon^b`.  Equation (32)
therefore evaluates a once-dotted sphere by `1` and an undotted sphere by
`0` on the whole source.  Cubic-order transport invariance removes every
`I+O(h)` correction.

## Remaining boundary

The relative sphere system is disjoint from the detector ball, the old
detector factor is fixed, and the actual sphere maps are computed by the
genus-zero/core-counit argument.  No historical sphere artifact is required.
