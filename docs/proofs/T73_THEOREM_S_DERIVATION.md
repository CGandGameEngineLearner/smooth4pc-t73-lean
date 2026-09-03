# Theorem S: relative standard-sphere consequence

**Status:** `DISCHARGED`

Paper Lemmas Ssystem and Sendpoint instantiate the total-kernel replacement
and the actual endpoint exchange square.

## Statement

Assume:

1. P0 gives the actual trace-73 handle presentation, with three 3-handles,
   one final 4-handle, and the detector supported in a boundary 3-ball `B`;
2. C gives a symmetric-monoidal coefficient-trace comparison natural for
   boundary cobordisms supported away from `B`.

Then the divided detector descends through all three MWW three-handle
coequalizers.

## Relative complete sphere system

Remove the final 4-handle and call the remaining handlebody `W3`.  Its
boundary is `S3`.  Reversing the three 3-handles attaches three
three-dimensional 1-handles, so

```text
partial W2 ~= #3(S1 x S2).
```

Choose the standard three nonseparating spheres outside `B`.  Their classes
form a basis of spherical second homology and their complement is connected.
Horvat--Jablonowski Theorem 5.3 identifies them with the actual attaching
system up to permutation, 3--3 handle slides and isotopy.  Lemma Ssystem
shows directly that these moves preserve the kernel of the total
three-handle map.  Thus the standard system can be used without applying an
ambient isotopy to the detector inside `B`.

## Intrinsic MWW closure

MWW's intrinsic module-action form of the three-handle theorem imposes, at
`N=2`,

```text
A0 = 1   (one-dotted essential sphere),
A1 = 0   (undotted essential sphere).
```

Monoidality alone is not enough because `A0,A1` are essential spheres.
Remove the `b` actual two-handle core disks from each sphere.  Its connected
genus-zero complement induces the iterated coproduct, and the core disks
induce `epsilon^b`.  Therefore on the whole source

```text
lambda(v A0) = lambda(v) ev(dotted S2) = lambda(v),
lambda(v A1) = lambda(v) ev(S2) = 0.
```

Hence the detector annihilates every MWW relation for each sphere and descends
through the iterated coequalizer.

## Scope

No TH1/TH2/THXY geometry file, signed slide decomposition, pivotal-adapter
ledger or endpoint permutation is used.  The optional owner lifts and
split-tree Lean algebra are compatible coordinate models but are not
load-bearing.

P0, C and S are supplied by the current paper.  See
`docs/research/T73_S_RELATIVE_STANDARD_SYSTEM_2026-09-02.md` for the
primary-source audit and detailed boundary conditions.
