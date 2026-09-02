# Standard-sphere MWW binding for the compact presentation

**Status:** `PARTIAL -- DERIVED FROM P0 AND MONOIDAL C`

This note records the compact replacement for the unavailable TH1/TH2/THXY
objects.  P0 is instantiated by the public AR witness; C remains open.

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

The full C comparison is required to be symmetric monoidal and natural for
cobordisms supported outside `B`.  Therefore, for every source element, the
detector row evaluates a disjoint one-dotted sphere by `1` and an undotted
sphere by `0`.  These whole-source identities give the MWW cocone for each of
the three standard spheres.

## Remaining boundary

No independent actual-sphere endpoint transport is required: the relative
sphere system and its neighborhoods are disjoint from the detector ball, so
the old detector factor is literally fixed.  Candidate-level closure still
waits on:

1. the embedded P0 witness and detector ball;
2. the actual symmetric-monoidal coefficient comparison C.

Once those are supplied, S follows without the historical sphere artifacts.
