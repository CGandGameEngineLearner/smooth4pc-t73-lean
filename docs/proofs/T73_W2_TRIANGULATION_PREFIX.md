# Verified prefix of a common post-cancellation boundary triangulation

Date: 2026-09-05

## Constructed prefix

`scripts/build_t73_reduced_boundary_prefix.py` constructs two explicit
triangulations of \(S^2\times S^1\). Each starts with the four-triangle
boundary of a tetrahedron and uses the staircase triangulation over three
cyclic interval layers. The builder deletes one tetrahedron from each
summand and identifies the two resulting boundary spheres by a reversed
vertex order. The output is a 20-vertex, 70-tetrahedron simplicial connected
sum.

The independent closed-complex checker verifies:

- every triangular face has multiplicity two;
- tetrahedron adjacency is connected;
- there are no duplicate tetrahedra or unused vertices;
- every vertex link is a connected triangulated 2-sphere.

Thus the finite construction is a closed combinatorial 3-manifold. By the
explicit connected-sum construction it is the canonical model
\[
\#^2(S^1\times S^2),
\]
the boundary type of a 4-dimensional 0/1-handlebody with two 1-handles.
The output also contains two vertex-disjoint three-edge loops labelled
\(y\) and \(z\); the checker derives that all of their edges occur in the
triangulation.

No assertion is made that this chosen canonical model is already connected
to the repository's post-cancellation attaching link.

## Deterministic two-handle boundary update

The same module implements `replay_dehn_filling_step`. Its standard solid
torus is
\[
(\operatorname{cone} C_3)\times S^1
\]
with a derived 27-tetrahedron staircase triangulation, an interior core
edge-loop, and explicit meridian and longitude edge-loops.

A filling step must exhibit:

1. tetrahedron indices and a vertex map identifying the removed neighborhood
   exactly with this solid torus;
2. the attaching component as the image of its core;
3. a second vertex map identifying the filling solid torus boundary
   simplicially with the exposed boundary;
4. three explicit fresh vertices for the filling solid torus's interior core,
   referenced by `new:0`, `new:1`, and `new:2`;
5. the canonical reindexing of source vertices that survive removal;
6. the framing curve as the image of the filling meridian;
7. the exact resulting closed triangulation.

The verifier removes the registered tetrahedra, drops the removed solid
torus's interior vertices, canonically compacts the surviving source indices,
appends the three genuinely new filling-core vertices, inserts the mapped
filling tetrahedra, and compares the full result. Reuse of a removed interior
vertex is rejected. A synthetic double-solid-torus example passes.
Meridian-to-longitude, removed-interior reuse, and boolean-only mutations are
rejected.

This is a deterministic simplicial model of the change in boundary caused by
attaching a 4-dimensional 2-handle. It does not infer a filling slope from a
word or blackboard integer.

## First unavailable embedding field

The current files contain a railroad embedding/PD description of the five
surviving components
\[
m_2,\ m_3,\ r_{xy},\ r_{yz},\ r_{zx}
\]
and separate framing metadata. They do not contain a common subdivision and
simplicial map placing those five curves and their framing annuli into the
20-vertex boundary complex above (or into any other explicit triangulation of
the reduced 0/1-handlebody boundary).

The first unavailable datum is therefore:

> A common subdivision \(K'\) of the canonical boundary and five
> pairwise-disjoint edge cycles in \(K'\), together with five embedded annulus
> subcomplexes realizing the transported framings and a checked map from every
> railroad segment/band owner to those subcomplexes.

Without this datum, the solid-torus neighborhoods and filling boundary maps
for the five deterministic Dehn-surgery steps cannot be formed. Attaching
words determine homotopy classes, not embedded framed curves, so no
fail-closed program can synthesize the missing map from the existing words
and hashes.

## Verification

Run:

```text
python3 -m unittest tests.test_t73_reduced_boundary_prefix
python3 scripts/build_t73_reduced_boundary_prefix.py --summary
```

The current output is 20 vertices, 70 tetrahedra, and boundary digest
`A389BDA2DDF42D88E504DFF694BA92CC19476A23D886FC19814A149D80CFAE49`.
