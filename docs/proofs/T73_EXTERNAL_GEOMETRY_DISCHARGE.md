# ExternalGeometry field-by-field discharge

**Status:** `PARTIAL -- P0/P3 AND RELATIVE S SUPPLIED; C OPEN`

> This file records a field allocation, not a Lean instance.  The public AR
> witness now supplies P0, published general theorems supply P3, and relative
> S follows from monoidal C.  The actual MWW coefficient comparison C remains
> open, so the complete external structures are not instantiated.

This note lists the mathematical fields used by
`Smooth4PC/T73External.lean` for the compact trace-73 presentation.  It does
not instantiate the remaining C fields and does not claim that skein lasagna
modules or smooth four-manifold topology have been formalized in Lean.

## Ambient universe

Let `Manifold` be the class of smooth compact oriented four-manifolds under
consideration and set

\[
G(M,q)=\mathcal S^2_{0,(0,q),0}(M;\varnothing;\mathbb Q),
\]

the rational `N=2` skein lasagna summand of homological degree zero, quantum
degree `q`, empty boundary link and zero absolute homology class.  Let
`candidate` be the closed compact AR presentation of `Sigma_A^0`, and let
`S4` be the standard sphere.

## One- and two-handle fields

Take `W0` to be the completed coefficient trace at the compact one-handle
stage before imposing the cabled beta/psi relations.  Theorem C constructs
the row `ell0` by the composite

\[
q\operatorname{Tr}(\mathcal C;M_R)
\xrightarrow{\mathsf C_h}
\operatorname{Hom}(V^{\otimes86},V^{\otimes88})
\xrightarrow{[h^3]\widehat C(\rho(W)-I)}\mathbb Q.
\]

Let `x0` be the Hattori class represented by
`Id_U tensor X^tensor227`.  The compact Hattori count, the endpoint comparison
and the public word calculation give

\[
\ell_0(x_0)=-59072
\]

after the harmless global row-sign normalization described in Theorem C.

Take `q01` to be the MWW cabled beta/psi quotient.  Theorem C's functorial
tangle action, simultaneous physical-copy transport, Reynolds normalization,
through-degree firewall and core-counit identities prove that `ell0` kills
the complete relation subspace.  The quotient universal property gives
`ell1` with

\[
\ell_1q_{01}=\ell_0.
\]

The exact Artin--Magnus certificate and Darn\'{e}'s Andreadakis equality show
that the base point-push belongs to `Gamma_3(P_44)`.  Every physical cabling
homomorphism preserves the lower central series, so the uniform order-three
divisibility used in this descent holds at every cable state, not only in the
public 88-dimensional base computation.

## Three-handle fields

The compact cellular boundary gives the unique five-owner lifts of the three
spherical basis classes.  The public Nielsen ledger constructs an embedded,
framed, pairwise-disjoint complete system, and the HJ theorem identifies it
with the actual attaching system up to three-handle moves.

Take `q12` to be the MWW coequalizer for this system.  Theorem S closes every
raw sphere movie with the same W2 core counits used in the target row.  Strict
functoriality reduces the composite to an undotted or once-dotted sphere, so
the row kills the two relations for each sphere.  The quotient universal
property gives `ell2` with

\[
\ell_2q_{12}=\ell_1.
\]

## Three-/four-handle transport

MWW Theorem 3.10 identifies the iterated cabled and sphere quotient with the
skein lasagna module after the three-handles.  Use this grading-preserving
identification as `transport`.  MWW Proposition 3.4 states that the final
four-handle induces an isomorphism; its inclusion map has bidegree `(0,0)`.
Its rational quantum-494 restriction is `fourIso`.

## Standard sphere and diffeomorphism invariance

MWW Corollary 3.5 gives

\[
\mathcal S^2_0(S^4)\cong\mathbb Z
\]

concentrated in bidegree `(0,0)`.  After tensoring with `Q`, every element in
quantum degree 494 is zero; this is `s4DegreeZero`.

Skein lasagna modules are defined intrinsically from lasagna fillings and
isotopy/cobordism relations.  A diffeomorphism transports fillings, input
balls, surfaces and labels and has an inverse transport.  It therefore
induces a grading-preserving linear equivalence; its quantum-494 restriction
is `diffeomorphismEquiv`.

## Cappell--Shaneson field

The compact AR presentation defines the candidate to be `Sigma_A^0` for the
displayed matrix.  Iwaki Proposition 2.1, restating the classical
Cappell--Shaneson criterion, says that `det(A-I)=+-1` is equivalent to this
construction being a homotopy sphere.  The Lean finite layer proves

\[
\det A=1,\qquad\det(A-I)=1.
\]

This supplies `matrixConditionsToHomotopySphere`.

## Conclusion

Every field of `ExternalGeometry` and `CSExternalGeometry` is now assigned to
a named construction or published theorem.  The Lean theorem then gives

\[
\operatorname{IsHomotopySphere}(\Sigma_A^0)
\quad\text{and}\quad
\Sigma_A^0\not\cong_{\mathrm{diff}}S^4.
\]

The mathematical conclusion depends on Theorems C and S as proved in the two
preceding notes.  The Lean kernel verifies only the finite algebra and the
logical use of these externally established fields.
