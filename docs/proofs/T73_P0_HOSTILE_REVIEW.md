# Hostile review of prop:unlabelled-P0 and thm:P0discharge

Date: 2026-09-05

## Verdict

After two corrections made during this review, the two results are sound as
paper-level existence theorems and do not need the obsolete global coordinate
PL evaluator. They establish the Cappell--Shaneson handle presentation and a
static marked product collar. They do not establish C, the coefficient shadow,
the auxiliary braid detector, or its quotient descent.

The corrections were load-bearing:

1. the relative section isotopy and epsilon parity are now constructed
   together by a point-fixed isotopy and parametric local straightening,
   rather than by merely declaring an even framing path;
2. the 42+2 passages are now tied to Johnson's actual embedded square-slide
   representatives and their parallel-lane realization, rather than inferred
   from abelianization or a free word alone.

## Clause-by-clause validation

### 1. The 93 factors are actual splitting-preserving mapping classes

Johnson defines two square-slide lifts of each elementary transvection: the
diagonal is pushed to either side of the coordinate square. Both are
orientation-preserving representatives preserving the genus-three splitting.
Thus every recorded side bit chooses an actual mapping class, not merely a
formal Nielsen substitution.

The finite factor verifier recomputes 93 unit transvections and their product
A. The side-search verifier recomputes the selected side word, the first spine
image z, the 311-letter m2 path, 42 y occurrences and exact agreement with the
compact word. These are valid finite calculations once each update is
interpreted as Johnson's square slide.

No global affine realization is required for this existence statement:
compose one representative of each of the 93 mapping classes.

### 2. The common section point is legitimate

The square-slide representatives can be chosen to fix the common coordinate
spine vertex q. Their product fixes q, which lies in the interior of one
handlebody. Local changes supported in a smaller interior ball do not affect
the Heegaard surface or interchange the handlebodies.

Given any ambient isotopy from the product to the linear representative,
compose at time s with translation by q minus the track of q. Since T3 is a
group and the track begins and ends at q, this gives a point-fixed isotopy
with unchanged endpoints. Intermediate translations need not preserve the
splitting; only the endpoint monodromies and the relative mapping-torus
identification are used.

### 3. Relative straightening and epsilon zero

The previous proof jumped from endpoint straightening to an isotopy relative
to a whole ball. That implication has a normal one-jet obstruction measured
by pi1(SO(3)). The corrected proof handles it explicitly.

Choose the local endpoint straightening class so that the derivative path of
the point-fixed isotopy closes to the null class. Parametric local
straightening then makes the entire isotopy constant on a smaller ball Bq.
The resulting mapping-torus diffeomorphism is the identity on Bq times S1.
It consequently carries the product normal framing exactly, not merely up to
an unspecified parity. This proves epsilon zero.

Choosing this class changes only the local straightening/isotopy data. It does
not change the endpoint mapping class, the matrix A, or the Johnson side word.
Thus there is no circular use of the desired framing.

### 4. Application of Aitchison--Rubinstein

The endpoint psi preserves the Heegaard pair and is identity on the section
ball, precisely the input needed for the AR handle construction. AR constructs
the mapping-handle attaching circles and framing annuli from actual cut spine
arcs and their images. Applying their recipe therefore gives a complete
embedded framed handle decomposition of the section surgery.

The relative mapping-torus isotopy from Clause 3 identifies that surgery with
Sigma_A^0. The determinant calculation is not used for this identification;
it is used only later to prove the identified object is a homotopy sphere.

### 5. The two one/two cancellations

The section-surgery handle meets the mapping-handle belt sphere once with its
product framing. Standard collar/general-position handle calculus slides the
finitely many other passages off before cancelling.

For the selected actual Johnson square-slide word, the image of the x spine
edge is the z edge path. After the first cancellation the corresponding core
is z followed by x inverse. In the product handle chart the z segment misses
the x belt and the bottom x inverse segment meets it once. Hence the second
pair satisfies the geometric cancellation criterion. The product framing
annuli determine relative twist zero.

The argument proves existence of suitable sequential bands. It does not
certify the repository's stored band centerlines, which is why the independent
coordinate band gate correctly remains open.

### 6. Upper handles

Every lower handle slide/cancellation induces a boundary diffeomorphism.
Transport the original AR three-handle attaching spheres and four-handle map
through those diffeomorphisms. Attaching the transported upper handles
therefore completes the same closed manifold. This is direct and avoids the
invalid language of one/three cancellation.

Laudenbach--Poenaru may alternatively remove the final upper-handle gluing
ambiguity after the boundary hypothesis is established. It is not being used
to recognize an unconstructed boundary.

### 7. Why the 42+2 passages are geometric

A reduced free word alone does not determine an embedded knot or its geometric
intersection number with a belt disk. The corrected proof does not make that
inference.

At each factor take Johnson's embedded diagonal square slide and apply isotopy
extension to the coordinate spine. Inductively, the oriented edge path is
updated by exactly the recorded Nielsen move. Repeated traversals are placed
in disjoint narrow parallel lanes in the regular neighborhood of the spine.
Thus the final embedded m2 path has one geometric lane for each of its
recorded letters, including exactly 42 y lanes. The standard embedded dual
cell r_xy has one positive and one negative y passage. This supplies 44
actual transverse passages before any standard collar coordinates are chosen.

The finite side-search replay confirms the combinatorial path and count; the
geometric implication comes from the square-slide induction and parallel-lane
construction, not from the output string PASS.

### 8. Static marked collar

For finitely many labelled transverse product arcs, a boundary-fixed
orientation-preserving diffeomorphism of the belt disk can send their distinct
points to any prescribed distinct rational configuration. Extend it by the
identity height coordinate. Disjoint tubular-neighborhood isotopies straighten
the product framings to the chosen constant normal.

The committed static-collar artifact uses an 11 by 4 rational grid, 44
vertical centre arcs, explicit positive push-offs and framing rectangles, and
88 ordered normal translates. Its verifier checks the 42+2 owner binding,
orientations, source IDs, disjointness, boundary levels and endpoint order,
and rejects six mutations. It contains no braid.

### 9. P0 conclusion and its boundary

The unlabelled proposition supplies Sigma_A^0 and all upper handles. The
marked-collar lemma supplies exactly the local product ball and cabled endpoint
marking required at P0. Therefore thm:P0discharge follows under the retyped
definition in which B44 belongs to C.

The theorem does not prove that the 44 y passages are paired with 44 particular
z passages by embedded product rectangles, that 227 leftover circles have
the asserted simultaneous product neighborhoods, or that the MWW coefficient
shadow exists. Those are C obligations. It also does not prove the S
hemisphere comparison. Promoting any of those statements into P0 would make
the proof circular again.

## Fresh finite replay

The hostile review reran:

    python3 scripts/search_t73_johnson_alpha_sides.py --check
    python3 scripts/factor_t73_matrix_johnson.py --check
    python3 scripts/verify_t73_p0_marked_vertical_collar.py --check

The outputs respectively confirmed the selected side word and 44 count, the
93-factor product A, and the static 44/88 collar with all six mutations
rejected. These checks support only the finite clauses stated above.
