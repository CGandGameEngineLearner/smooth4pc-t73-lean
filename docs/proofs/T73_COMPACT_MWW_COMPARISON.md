# Compact Burau--MWW comparison

**Status:** `SUPERSEDED BY THE COMPLETE THEOREM C DERIVATION`

This note collects the public compact replacement for the missing cable and
Hattori artifacts.

## Balanced cable count

The compact Aitchison--Rubinstein word generator gives

\[
\#_{y,Y}(m_2)=42,\qquad \#_{z,Z}(m_2)=269.
\]

For `r_xy=[z,y]`, the corresponding counts are two and two.  Hence the
selected balanced `m_2/r_xy` cable state has

\[
p_y=42+2=44,qquad p_z=269+2=271.
\]

Pair the 44 y-wickets with 44 z passages using product subrectangles of the
parallel cable annuli.  The remaining z passages close into

\[
p_z-p_y=227
\]

ordered product circles.  Oppositely oriented cable copies double the y
endpoint count to 88.  All framings are restrictions of the AR
product-annulus normal.

The complete replay is:

```text
python -B scripts/verify_t73_compact_hattori_binding.py
python -I -B tests/test_t73_compact_hattori_binding.py -v
```

Its current ledger identity is

```text
BE833E1725AC353EFC49A7C83FB08254CDE2D5924A4FD9168225E6ABB14F5169
```

## Hattori coefficient

If the actual west-to-east product motion is `B_act`, the two boundary
components of each product annulus give the same physical motion with
opposite pivotal orientation.  In that case the cut coefficient has the
framed normal form

\[
R\simeq B_{act}\sqcup B_{act}^{\vee}\sqcup U^{227},
\qquad B_{act}^{\vee}\cong B_{act}^{-1}.
\]

However, `B_act` cannot be set equal to the public braid merely by choosing
east coordinates.  A coordinate change `P` must simultaneously transport

\[
W\mapsto PWP^{-1},\qquad u\mapsto Pu,\qquad
\ell\mapsto\ell P^{-1}.
\]

Holding the public `W,u,ell` fixed while changing only `B_act` is illegal and
would manufacture the same apparent anomaly in unrelated handlebodies.
Therefore the public counts do not yet establish the following two-sided
coefficient equivalence for the actual product motion:

\[
M_R(T,T')\cong
\operatorname{Hom}(B_{act}T,B_{act}T')\{-44\}
\otimes A^{\otimes227}.
\]

Once the actual simultaneous transport `P` is constructed, left and right
action naturality will be the two gluing boundaries of the same product
isotopy, and BPW/BHPW functoriality will apply without a separate sign choice.

For

\[
T_1=B_{act}^{-1}U,qquad T_0=B_{act}^{-1}WU,
\]

the product cancellation gives `B_act T1=U` and `B_act T0=WU`.  The selected
Hattori class is consequently represented by

\[
Id_U\otimes X^{\otimes227}.
\]

## Endpoint representation

`Smooth4PC/BurauRMatrix.lean` proves the local representation comparison.
On the weight-one two-site subspace, the normalized checked R-matrix is

\[
\begin{pmatrix}1-q^{-2}&q^{-1}\\q^{-1}&0\end{pmatrix}.
\]

After the position-dependent basis change `diag(1,q^-1)` and the substitution
`t=q^-2`, it becomes

\[
\begin{pmatrix}1-t&t\\1&0\end{pmatrix},
\]

exactly the positive block in `scripts/recompute_t73_delta3.py`.  The file
also proves that the script's negative block is its inverse.

BHPW proves that the Chen--Khovanov algebras categorify the tensor-product
weight spaces and, over flat coefficients, that the Chern character from
their Grothendieck group to quantum `HH0` is an isomorphism.  Thus the local
matrix is the action on the Chern/weight-space target, not merely a numerical
similarity.  One further comparison is still required: the MWW coefficient
trace after the product Hattori equivalence must be shown to land in this
specific quantum `HH0` Chern summand, with the completion
`q -> 1+h` and all grading shifts commuting.  The local matrix theorem alone
does not construct that arrow.

## Retained quotient boundary

Uniform divisibility is independently checked on the full endpoint module:

```text
python -B scripts/verify_t73_uniform_order3.py
python -I -B tests/test_t73_uniform_order3.py -v
```

The verifier evaluates all 88 basis vectors and all 7,744 matrix entries and
finds no coefficient in orders zero, one or two.  Thus division by `h^3` is
defined on the whole endpoint target, not merely on the selected vector.  A
mutation deleting one Artin letter is rejected.

A negative control is public:

```text
python -B scripts/check_t73_naive_endpoint_reynolds.py
```

It proves that averaging all 44 even and all 44 odd endpoint passages kills
the complete h-series pairing.  This is not the MWW beta average.  Therefore
the one-handle `S_44^- x S_44^+` relations must be handled by BPW
coefficient-trace cyclicity, while beta uses only ownerwise physical cable
copies.  Conflating these two quotients destroys the selected signal.

The construction above supplies the balanced cable counts and the local
R-matrix/Burau comparison.  It does not supply the actual coefficient class
until the product-motion matrix `P` and the three simultaneous transport
equalities are proved.  After that, the Reynolds/counit rows and the
three-handle maps still have to be bound.  The finite cubic algebra for those
steps is kernel checked, but this note does not instantiate the complete MWW
quotient.
